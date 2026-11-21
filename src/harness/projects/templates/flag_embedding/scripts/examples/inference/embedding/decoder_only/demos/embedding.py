"""Decoder-only embedding examples shared by the direct and automatic launchers."""

from os import getenv

from FlagEmbedding import FlagAutoModel, FlagICLModel, FlagLLMModel, FlagPseudoMoEModel

QUESTION_INSTRUCTION = "Given a question, retrieve passages that answer the question."


QUERIES = [
    'how much protein should a female eat',
    'summit define',
]

PASSAGES = [
    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
    'Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments.',
]

PSEUDO_MOE_PASSAGES = [
    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day.",
    'Definition of summit for English Language Learners: the highest point of a mountain; the highest level; a meeting between leaders.',
]

ICL_EXAMPLES = [
    {
        'instruct': 'Given a web search query, retrieve relevant passages that answer the query.',
        'query': 'what is a virtual interface',
        'response': 'A virtual interface is a software-defined abstraction that mimics the behavior and characteristics of a physical network interface. It allows multiple logical network connections to share the same physical network interface, enabling efficient utilization of network resources. Virtual interfaces are commonly used in virtualization technologies such as virtual machines and containers to provide network connectivity without requiring dedicated hardware. They facilitate flexible network configurations and help in isolating network traffic for security and management purposes.',
    },
    {
        'instruct': 'Given a web search query, retrieve relevant passages that answer the query.',
        'query': 'causes of back pain in female for a week',
        'response': 'Back pain in females lasting a week can stem from various factors. Common causes include muscle strain due to lifting heavy objects or improper posture, spinal issues like herniated discs or osteoporosis, menstrual cramps causing referred pain, urinary tract infections, or pelvic inflammatory disease. Pregnancy-related changes can also contribute. Stress and lack of physical activity may exacerbate symptoms. Proper diagnosis by a healthcare professional is crucial for effective treatment and management.',
    },
]


def _show_similarity(model, passages, batch_repeats):
    query_embeddings = model.encode_queries(QUERIES * batch_repeats)
    passage_embeddings = model.encode_corpus(passages * batch_repeats)
    similarities = query_embeddings @ passage_embeddings.T
    print(similarities[:2, :2])


def show_base(devices, *, automatic):
    load = FlagAutoModel.from_finetuned if automatic else FlagLLMModel
    options = {} if automatic else {"query_instruction_format": "<instruct>{}\n<query>{}"}
    model = load(
        "BAAI/bge-multilingual-gemma2",
        query_instruction_for_retrieval=QUESTION_INSTRUCTION,
        devices=devices,
        cache_dir=getenv("HF_HUB_CACHE"),
        **options,
    )
    _show_similarity(model, PASSAGES, batch_repeats=100)


def show_icl(devices, *, automatic):
    load = FlagAutoModel.from_finetuned if automatic else FlagICLModel
    options = {} if automatic else {"query_instruction_format": "<instruct>{}\n<query>{}"}
    model = load(
        "BAAI/bge-en-icl",
        query_instruction_for_retrieval=QUESTION_INSTRUCTION,
        examples_for_task=ICL_EXAMPLES,
        examples_instruction_format="<instruct>{}\n<query>{}\n<response>{}",
        devices=devices,
        cache_dir=getenv("HF_HUB_CACHE"),
        **options,
    )
    _show_similarity(model, PASSAGES, batch_repeats=100)


def show_pseudo_moe(devices, *, automatic, domain, batch_repeats):
    load = FlagAutoModel.from_finetuned if automatic else FlagPseudoMoEModel
    options = {"model_class": "decoder-only-pseudo_moe"} if automatic else {}
    model = load(
        "geevec-ai/geevec-embeddings-1.0-lite",
        query_instruction_for_retrieval=QUESTION_INSTRUCTION,
        query_instruction_format="Instruct: {}\nQuery: {}",
        domain_for_pseudo_moe=domain,
        use_fp16=False,
        use_bf16=True,
        trust_remote_code=True,
        devices=devices,
        cache_dir=getenv("HF_HUB_CACHE"),
        **options,
    )
    _show_similarity(model, PSEUDO_MOE_PASSAGES, batch_repeats)
