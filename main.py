from pipeline.pipeline import run_pipeline


def main():

    query = input("Enter your query: ")

    state = run_pipeline(query)

    print("\n========== PLAN ==========\n")
    print(state["plan"])

    print("\n========== RESEARCH ==========\n")
    print(state["research"])

    print("\n========== ANALYSIS ==========\n")
    print(state["analysis"])

    print("\n========== CHARTS ==========\n")
    print(state["visualization"])

    print("\n========== REPORT ==========\n")
    print(state["report"])


if __name__ == "__main__":
    main()