import boto3, requests, base64

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("nadialin-hunters")

def cache_google_image(user_id, image_url):
    # Fetch the image
    resp = requests.get(image_url)
    resp.raise_for_status()
    img_bytes = resp.content

    # Store in DynamoDB
    table.put_item(
        Item={
            "name": user_id,
            "pictureBytes": img_bytes,   # boto3 auto-handles Binary
            "CachedAt": int(__import__("time").time())
        }
    )

# Example usage
cache_google_image("kengraf57", "https://lh3.googleusercontent.com/a/ACg8ocLQ3brj76ujujP8i5s21BMGS4w4p3_tzTperrtJdtTNQlJKIc9a=s96-c")
