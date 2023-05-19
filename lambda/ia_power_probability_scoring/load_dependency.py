import boto3
import os
import sys
import zipfile

pkgdir = "/tmp/ia-sklearn-small-layer"
zip_requirements = "/tmp/ia-sklearn-layer.zip"

sys.path.append(pkgdir)

if os.environ.get("AWS_EXECUTION_ENV") is not None:
    if not os.path.exists(pkgdir):

        s3 = boto3.resource("s3")
        bucket = s3.Bucket("ia-dev-sandbox-1")
        bucket.download_file("lib/ia-sklearn-small-layer.zip", zip_requirements)

        zipfile.ZipFile(zip_requirements, "r").extractall(pkgdir)

        os.remove(zip_requirements)
        print(os.listdir("/tmp/"))
        print(os.listdir("/tmp/ia-sklearn-small-layer/"))

        sys.path.append(
            "/tmp/ia-sklearn-small-layer/python/lib/python3.8/site-packages/"
        )
