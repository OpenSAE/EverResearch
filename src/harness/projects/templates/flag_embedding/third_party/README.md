# Upstream research releases

The [FlagEmbedding research releases](flag_embedding_research/README.md) are the upstream `research/` tree at commit `897baa67c0ffddbfccf4e6776ff55310d67809d4`. This checkout keeps their files and internal paths intact so their original package discovery, inputs, and reproduction recipes stay together. The upstream license and any project-specific licenses continue to apply.

Run release-local commands from the corresponding directory under `third_party/flag_embedding_research/`. When a published instruction starts with `cd FlagEmbedding/research/<release>`, use `cd third_party/flag_embedding_research/<release>` from this checkout's root. To reproduce a command that assumes the old root layout, use a worktree at the upstream commit above.

| Release directories | Contents |
| --- | --- |
| BGE_Coder, BGE_M3, BGE_Reasoner, BGE_VL, BGE_VL_Screenshot, visual_bge | Model papers, visual assets, released implementations, and reproducible examples |
| C_MTEB, MLVU | Benchmark adapters, scripts, and sample inputs |
| LLARA, LM_Cocktail, Long_LLM, Matroyshka_reranker, Reinforced_IR | Standalone training, inference, or evaluation programs for the corresponding papers |
| baai_general_embedding, llm_dense_retriever, llm_embedder, llm_reranker, reranker | Published retrieval and fine-tuning releases, including the in-context examples used by current MTEB recipes |
| old-examples | Historical recipes for specific published model revisions |
