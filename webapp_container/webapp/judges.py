from mlflow.genai.scorers import RelevanceToQuery, RetrievalRelevance, ScorerSamplingConfig
from parameters import judge_id, token, judges_sample_rate

relevance_to_query_judge = RelevanceToQuery(model="gateway:/test")

retrieval_relevance_judge = RetrievalRelevance(model="gateway:/test")

scorer_sampling = ScorerSamplingConfig(sample_rate=judges_sample_rate)
