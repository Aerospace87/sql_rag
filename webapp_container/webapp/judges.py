from mlflow.genai.scorers import RelevanceToQuery, ScorerSamplingConfig
from parameters import judge_id, token, judges_sample_rate

relevance_to_query_judge = RelevanceToQuery(model="gateway:/test")

scorer_sampling = ScorerSamplingConfig(sample_rate=judges_sample_rate)
    
