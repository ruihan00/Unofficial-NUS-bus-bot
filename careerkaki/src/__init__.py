import json
from pathlib import Path

import chromadb
import pandas as pd
from langchain.embeddings import VertexAIEmbeddings
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

memory = {}
recap_needed = True
VERTEX_AI_EMBEDDING_MODEL = 'textembedding-gecko@003'
client = OpenAI()
GPT_MODEL = "gpt-3.5-turbo-0613"

DATA_FOLDER = Path('./data/')
target_job_roles_df = pd.read_pickle(
    DATA_FOLDER / "ict_or_retail_job_roles_df.pkl")

target_job_roles_ids, target_job_roles_embeddings, target_job_roles_salary_p10, target_job_roles_salary_p90, target_job_roles_skills = (
    target_job_roles_df['job_role'].to_list(),
    target_job_roles_df['embeddings'].to_list(),
    [row['10'] for row in target_job_roles_df['salary']],
    [row['90'] for row in target_job_roles_df['salary']],
    target_job_roles_df['skills'].to_list(),
)

# Read Job Roles
job_roles_df = pd.read_pickle(
    DATA_FOLDER / "job_roles_df.pkl")

job_roles_ids, job_roles_embeddings, job_roles_salary_p10, job_roles_salary_p90, job_roles_skills = (
    job_roles_df['job_role'].to_list(),
    job_roles_df['embeddings'].to_list(),
    [row['10'] for row in job_roles_df['salary']],
    [row['90'] for row in job_roles_df['salary']],
    job_roles_df['skills'].to_list(),
)
# Read Educations
educations_df = pd.read_pickle(
    DATA_FOLDER / "educations_df.pkl")
educations_ids, educations_embeddings, educations_salary_p10, educations_salary_p90, educations_skills = (
    educations_df['edu'].to_list(),
    educations_df['embeddings'].to_list(),
    [row['10'] for row in educations_df['salary']],
    [row['90'] for row in educations_df['salary']],
    educations_df['skills'].to_list(),
)


class VertexAIEmbeddingFunction(chromadb.EmbeddingFunction):
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        model = VertexAIEmbeddings(model_name=VERTEX_AI_EMBEDDING_MODEL)
        embeddings = model.embed_documents(texts=input)
        return embeddings


vertextai_emb_fn = VertexAIEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path='./data/chromadb/')

target_job_role_collection = chroma_client.get_or_create_collection(
    name="target_job_roles",
    embedding_function=vertextai_emb_fn,
    metadata=None
)

job_role_collection = chroma_client.get_or_create_collection(
    name="job_roles",
    embedding_function=vertextai_emb_fn,
    metadata=None
)

education_collection = chroma_client.get_or_create_collection(
    name="educations",
    embedding_function=vertextai_emb_fn,
    metadata=None
)

target_job_role_collection.upsert(
    embeddings=target_job_roles_embeddings,
    documents=target_job_roles_ids,
    metadatas=[{
        "min_salary": item[0],
        "max_salary": item[1],
        "skills": json.dumps(item[2]),
    } for item in zip(target_job_roles_salary_p10, target_job_roles_salary_p90, target_job_roles_skills)],
    ids=target_job_roles_ids,
)

job_role_collection.upsert(
    embeddings=job_roles_embeddings,
    documents=job_roles_ids,
    metadatas=[{
        "min_salary": item[0],
        "max_salary": item[1],
        "skills": json.dumps(item[2]),
    } for item in zip(job_roles_salary_p10, job_roles_salary_p90, job_roles_skills)],
    ids=job_roles_ids,
)

education_collection.upsert(
    embeddings=educations_embeddings,
    documents=educations_ids,
    metadatas=[{
        "min_salary": item[0],
        "max_salary": item[1],
        "skills": json.dumps(item[2]),
    } for item in zip(educations_salary_p10, educations_salary_p90, educations_skills)],
    ids=educations_ids,
)


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


attributes = ['target_job_role', 'education',
              'prior_work_experiences', 'work_preferences']
