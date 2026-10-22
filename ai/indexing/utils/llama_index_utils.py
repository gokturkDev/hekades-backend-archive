from llama_index.core.schema import TextNode, NodeWithScore

from business.entity.source.source_chunk import SourceChunk


def text_node_to_chunk(node: TextNode) -> SourceChunk:
    source_id = node.metadata.pop("source_id")
    summary = node.metadata.pop("hekades_summary")
    return SourceChunk(
        source_id=source_id,
        chunk_id=node.node_id,
        content=node.text,
        summary=summary,
        metadata=node.metadata
    )


def chunk_to_text_node(chunk: SourceChunk) -> NodeWithScore:
    return NodeWithScore(
        node=TextNode(
            text=chunk.content,
            metadata=chunk.metadata | {"source_id": chunk.source_id},
        ),
        score=5 - chunk.score,
    )
