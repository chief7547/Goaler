from core.conversation_summary import ConversationSummarizer


def _fake_summary(logs):
    return f"총 {len(list(logs))}개 메시지를 요약했습니다."


def test_summariser_no_summary_when_below_threshold(storage):
    summariser = ConversationSummarizer(storage, _fake_summary, threshold=5, keep_latest=2)
    conv_id = "conv-low"
    for idx in range(3):
        storage.create_conversation_log(
            {
                "conversation_id": conv_id,
                "role": "user" if idx % 2 == 0 else "assistant",
                "content": f"메시지 {idx}",
            }
        )

    result = summariser.summarise_if_needed(conv_id)
    assert result is None
    assert storage.count_conversation_logs(conv_id) == 3
    assert storage.list_conversation_summaries(conv_id) == []


def test_summariser_trims_and_saves_summary(storage):
    summariser = ConversationSummarizer(storage, _fake_summary, threshold=5, keep_latest=2)
    conv_id = "conv-high"
    for idx in range(6):
        storage.create_conversation_log(
            {
                "conversation_id": conv_id,
                "role": "user",
                "content": f"내용 {idx}",
                "token_count": idx,
            }
        )

    summary_text = summariser.summarise_if_needed(conv_id)
    assert summary_text is not None

    summaries = storage.list_conversation_summaries(conv_id)
    assert len(summaries) == 1
    assert "요약" in summaries[0]["summary_text"]

    remaining = storage.count_conversation_logs(conv_id)
    assert remaining == 2
