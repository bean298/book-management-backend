import re

FROM = (
    "áàảãạâấầẩẫậăắằẳẵặ"
    "óòỏõọôốồổỗộơớờởỡợ"
    "éèẻẽẹêếềễệ"
    "úùủũụưứừửữự"
    "íìỉĩị"
    "ýỳỷỹỵ"
    "đ"
)

TO = (
    "aaaaaaaaaaaaaaaaaooooooooooooooooo" "eeeeeeeeeee" "uuuuuuuuuuu" "iiiii" "yyyyy" "d"
)


# Build slug for book
def build_slug(input: str) -> str:
    output = input.strip().lower()

    # Remove Vietnamese diacritics
    for i in range(len(FROM)):
        output = output.replace(FROM[i], TO[i])

    # Remove special characters
    output = re.sub(r"[^\w ]+", "", output)

    # One or more spaces -> "-"
    output = re.sub(r" +", "-", output)

    return output
