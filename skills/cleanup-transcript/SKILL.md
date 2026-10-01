---
name: cleanup-transcript
description: Produce a polished mirror of a machine-generated transcript
---

You have been provided with a machine-generated transcript for an audio recording of a conversation between multiple parties.

You may have also been provided supporting information as context for the conversation in order to identify terms and the speakers at each point.

Your task is to produce a cleaned up version of the transcript that labels the speaker, fixes the transcript errors and creates a polished mirror of what was said.

You may make small fixes to grammar and punctuation, but do not paraphrase or substitute the speaker's words.

We want to preserve the colour of what was said and the speaker's original phrasing whilst trimming the noise, such as: stutters, forced starts, excessive filler words or transcript errors.

Do not include any preamble in your response. It should be a markdown file complete beginning with a title for the meeting and the date it occurred if that information is available.