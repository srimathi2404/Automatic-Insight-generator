class AnalysisAgent:

    def __init__(
        self,
        explorer,
        llm
    ):
        self.explorer = explorer
        self.llm = llm

    def analyze_table(
        self,
        table
    ):

        schema = self.explorer.get_schema(table)

        row_count = self.explorer.get_row_count(table)

        sample = self.explorer.sample_rows(table)

        return {
            "schema": schema,
            "row_count": row_count,
            "sample": sample
        }