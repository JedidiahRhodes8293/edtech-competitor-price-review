from price_watch_service import CourseOffer, review_offers


def test_report_flags_only_offer_over_ceiling():
    offers = [CourseOffer("a", "Intro", "A", 100.0, 10), CourseOffer("b", "Advanced", "B", 100.01, 5)]
    result = review_offers(offers, ceiling=100.0)
    assert [row["decision"] for row in result] == ["track", "review"]
