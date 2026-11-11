#!/usr/bin/env bash
# Publish the gallery to S3 + CloudFront (docs: spatialscape "Hosting"). Settings in deploy/aws.env.
#   publish.sh setup     one time: the private bucket, its CORS, the CloudFront distribution reading it
#   publish.sh bundles   upload every bundle: from the cluster (ssh, the bundles never touch the laptop),
#                        the DLPFC and PBMC ones from this machine, atera copied inside S3 from the LIBD bucket
#   publish.sh site      build the viewer + datasets.json with data_url and upload them, then invalidate
# Credentials: `aws login --profile organoid-login` first; everything runs as $PROFILE (a role from that login).
set -euo pipefail
cd "$(dirname "$0")"
source aws.env
export AWS_PROFILE=$PROFILE
EXCLUDE=(--exclude "*/build.json" --exclude "build-info.json")
CLUSTER_APPS=(abc-atlas cosmx-nsclc merscope-mouse-brain spatial-atac-rna-mouse-brain visium-cytassist-mouse-brain visium-hd-mouse-brain xenium-mouse-brain)

case "${1:-}" in
setup)
  aws s3api create-bucket --bucket "$BUCKET" --region us-east-1
  aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
  aws s3api put-bucket-cors --bucket "$BUCKET" --cors-configuration '{"CORSRules":[{"AllowedOrigins":["*"],"AllowedMethods":["GET","HEAD"],"AllowedHeaders":["Range","Content-Type","Origin"],"ExposeHeaders":["Content-Range","Content-Length","Accept-Ranges","ETag"],"MaxAgeSeconds":86400}]}'
  OAC=$(aws cloudfront create-origin-access-control --origin-access-control-config "Name=$BUCKET,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3" --query OriginAccessControl.Id --output text)
  RHP=$(aws cloudfront list-response-headers-policies --type custom --query "ResponseHeadersPolicyList.Items[?ResponseHeadersPolicy.ResponseHeadersPolicyConfig.Name=='spatialscape-cors-range'].ResponseHeadersPolicy.Id | [0]" --output text)
  [ "$RHP" != None ] || RHP=$(aws cloudfront create-response-headers-policy --response-headers-policy-config '{"Name":"spatialscape-cors-range","CorsConfig":{"AccessControlAllowOrigins":{"Quantity":1,"Items":["*"]},"AccessControlAllowHeaders":{"Quantity":3,"Items":["Range","Content-Type","Origin"]},"AccessControlAllowMethods":{"Quantity":3,"Items":["GET","HEAD","OPTIONS"]},"AccessControlAllowCredentials":false,"AccessControlExposeHeaders":{"Quantity":4,"Items":["Content-Range","Content-Length","Accept-Ranges","ETag"]},"AccessControlMaxAgeSec":86400,"OriginOverride":true}}' --query ResponseHeadersPolicy.Id --output text)
  ORIGIN="$BUCKET.s3.us-east-1.amazonaws.com"
  # managed policies: CachingOptimized 658327ea-f89d-4fab-a63d-7e88639e58f6, CORS-S3Origin 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf
  ID=$(aws cloudfront create-distribution --distribution-config "$(cat <<JSON
{"CallerReference":"$BUCKET-$(date +%s)","Comment":"spatialscape examples","Enabled":true,"DefaultRootObject":"index.html","HttpVersion":"http2and3","PriceClass":"PriceClass_All",
 "Origins":{"Quantity":1,"Items":[{"Id":"s3","DomainName":"$ORIGIN","OriginAccessControlId":"$OAC","S3OriginConfig":{"OriginAccessIdentity":""}}]},
 "DefaultCacheBehavior":{"TargetOriginId":"s3","ViewerProtocolPolicy":"redirect-to-https","Compress":true,
   "AllowedMethods":{"Quantity":3,"Items":["GET","HEAD","OPTIONS"],"CachedMethods":{"Quantity":3,"Items":["GET","HEAD","OPTIONS"]}},
   "CachePolicyId":"658327ea-f89d-4fab-a63d-7e88639e58f6","OriginRequestPolicyId":"88a5eaf4-2fd4-4709-b370-b4c650ea3fcf","ResponseHeadersPolicyId":"$RHP"}}
JSON
)" --query Distribution.Id --output text)
  DOMAIN=$(aws cloudfront get-distribution --id "$ID" --query Distribution.DomainName --output text)
  ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
  aws s3api put-bucket-policy --bucket "$BUCKET" --policy "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"cloudfront.amazonaws.com\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$BUCKET/*\",\"Condition\":{\"StringEquals\":{\"AWS:SourceArn\":\"arn:aws:cloudfront::$ACCOUNT:distribution/$ID\"}}}]}"
  echo "distribution $ID at https://$DOMAIN -- put both in aws.env and as data_url in site.yaml" ;;
bundles)
  echo "-- from the cluster"   # the login's temporary credentials go over ssh on stdin, never into a file or a command line;
  for ds in "${CLUSTER_APPS[@]}"; do   # they last minutes, so each attempt gets fresh ones and a sync cut off by expiry is resumed
    echo "-- $ds"; n=0
    until aws configure export-credentials --format env | ssh "$CLUSTER" "source /dev/stdin; module load aws/2.28 >/dev/null 2>&1
        cd $CLUSTER_APPS_DIR && aws s3 sync $ds s3://$BUCKET/$ds --only-show-errors ${EXCLUDE[*]}"; do
      n=$((n + 1)); [ $n -lt 40 ] || { echo "$ds: giving up after $n attempts"; exit 1; }; echo "   $ds: resuming with fresh credentials"
    done
  done
  echo "-- visium-human-dlpfc and pbmc-multiome from this machine"
  for ds in visium-human-dlpfc pbmc-multiome; do
    aws s3 sync "../$ds/bundles/$ds" "s3://$BUCKET/$ds" --only-show-errors "${EXCLUDE[@]}"
  done
  echo "-- atera, copied inside S3 from $LIBD_BUCKET"
  aws s3 sync "s3://$LIBD_BUCKET/atera" "s3://$BUCKET/atera" --only-show-errors ;;
site)
  spatialscape site build site.yaml -o ../site
  aws s3 sync ../site "s3://$BUCKET/" --delete --exclude "*/*" --only-show-errors     # only the top level and assets/: the bundles stay
  aws s3 sync ../site/assets "s3://$BUCKET/assets" --delete --only-show-errors
  aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" --paths "/index.html" "/datasets.json" "/favicon.svg" "/assets/*" --query Invalidation.Id --output text ;;
*) sed -n '2,8p' "$0"; exit 1 ;;
esac
