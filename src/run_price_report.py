import json

from price_watch_service import CourseOffer, review_offers


def main() -> None:
    offers = [
        CourseOffer("python-101", "Python foundations", "Northstar Learning", 89.0, 14),
        CourseOffer("data-201", "Applied data analysis", "Cedar Academy", 129.0, 7),
    ]
    print(json.dumps(review_offers(offers), indent=2))


if __name__ == "__main__":
    main()
