from mlflow.genai.scorers import RelevanceToQuery, RetrievalRelevance, ScorerSamplingConfig
from mlflow.genai.judges import make_judge
from parameters import judge_id, token, judges_sample_rate
from typing import Literal
from prompts import prompt_retrieval_relevance_judge

relevance_to_query_judge = RelevanceToQuery(model="gateway:/test")

scorer_sampling = ScorerSamplingConfig(sample_rate=judges_sample_rate)

retrieval_relevance_judge = make_judge(
    name="retrieval_relevance_judge",
    instructions= prompt_retrieval_relevance_judge(),
    feedback_value_type=Literal["Pass", "Fail"],
    model="gateway:/test"
)



   
    
