import json
from pathlib import Path

from search import handle_search


TEST_FILE = Path(__file__).resolve().with_name("search_tests.json")


def load_tests():
    """Load search regression tests."""

    with TEST_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_tests():

    tests = load_tests()

    passed = 0
    failed = 0

    supported_total = 0
    supported_passed = 0

    irrelevant_total = 0
    irrelevant_passed = 0

    unsafe_total = 0
    unsafe_passed = 0

    print("=" * 70)
    print("MPS SEARCH TESTS")
    print("=" * 70)

    for test in tests:

        query = test["query"]
        expected = test["expected"]
        test_type = test["type"]

        search_result = handle_search(query)
        results = search_result["results"]
        blocked = search_result["blocked"]

        # Get the top result if one exists
        if results:
            actual = results[0]["resource_id"]
            top_name = results[0]["resource_name"]
            top_score = results[0]["score"]
            #top_intent_score = results[0]["intent_score"]
            top_semantic_score = results[0]["semantic_score"]
        else:
            actual = None
            top_name = "No result"
            top_score = 0.0
            #top_intent_score = 0.0
            top_semantic_score = 0

        if test_type == "unsafe":
            # Unsafe queries must be explicitly blocked
            test_passed = blocked and len(results) == 0

        elif test_type == "irrelevant":

            # Irrelevant queries should return nothing,
            # but should NOT be treated as unsafe
            test_passed = not blocked and len(results) == 0

        elif test_type == "supported":

            # Supported queries should not be blocked and
            # should return the expected resource first
            test_passed = (
                not blocked
                and actual == expected
            )

        else:
            test_passed = False

        # Determine whether the test passed
        if expected is None:
            test_passed = len(results) == 0
        else:
            test_passed = actual == expected

        if test_passed:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        # Track performance by test type
        if test_type == "supported":
            supported_total += 1

            if test_passed:
                supported_passed += 1

        elif test_type == "irrelevant":
            irrelevant_total += 1

            if test_passed:
                irrelevant_passed += 1

        elif test_type == "unsafe":
            unsafe_total += 1

            if test_passed:
                unsafe_passed += 1

        print()
        print(f"[{status}] {query}")
        print(f"  Type:     {test_type}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        print(f"  Result:   {top_name}")
        print(f"  Score:    {top_score:.3f}")
        #print(f"  Intent:   {top_intent_score:.3f}")
        print(f"  Semantic: {top_semantic_score:.3f}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(tests)

    print(f"Overall:    {passed}/{total} passed")

    if supported_total:
        print(
            f"Supported:  "
            f"{supported_passed}/{supported_total} passed"
        )

    if irrelevant_total:
        print(
            f"Irrelevant: "
            f"{irrelevant_passed}/{irrelevant_total} passed"
        )

    if unsafe_total:
        print(
            f"Unsafe:     "
            f"{unsafe_passed}/{unsafe_total} passed"
        )

    print(f"Failed:     {failed}")


if __name__ == "__main__":
    run_tests()