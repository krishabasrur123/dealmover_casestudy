# AI Usage Disclosure

## Tools Used
- ChatGPT (OpenAI)
- GitHub Copilot

## Youtube Links Reffered To (partial code was taken and adapted from here)
### PDF Upload
https://www.youtube.com/watch?v=5Yglpim64JQ
https://www.youtube.com/watch?v=KQJRwWpP8hs&list=PLTsuo31TJ3T4TVESMcYsWNehx9KNnAVDC
https://www.youtube.com/shorts/xOwzORR-uJ4

### App setup
https://www.youtube.com/watch?v=nGIg40xs9e4


## Prompts 

1. Asing Chatgpt to break down spec, make sure I did not miss any requirements
2. Asking standard 10-K formats, explain details of the given 10-K document, and clear steps where I would find revenue and cost
3. Differences between different text parsers (ex Regex vs Table Parsers )
4. Debug runtime or compilation issues throughout the project by pasting the error message in the prompt and asking what may be causing the issue

5. Asking to create complex regex patterns and extract captured groups to find certain lines (ex Consolidated Statements)

6. Asking to debug and refine the code when my raw code deosn't go well

7. Show me how Pytests work (what imports I need, how to set up the pdf loaders, how to write a test)

8. Give me suggestions on how to speed up (Previously, our implementation parsed the entire PDF before searching for specific headers. To speed things up, we now stop parsing once we reach the last page relevant to the requested section. This avoids unnecessary processing of unneeded pages)


## Accepted Rejected Outputs

Accepted outputs consisted of those where I can fully understand what the AI had implemented in the form of code or explained when in need of debugging any code. While I worked on the overall algorithm and thought process, AI tools mainly helped me catch mistakes and better understand what changes could improve my implementation. I reviewed each suggestion carefully, accepting ones that aligned with my reasoning and rejecting those that didn’t fit the requirements. For example, while the AI suggested I can simply use regex to find the certain headers "Item 8" etc, I knew that 10-K documents were complex and trying to search through every page looking for headers would take time. Thus, my idea was to look for the first Item 8 header, look for the page number, and if we can extract the page number from all the pages we can search for the other headers that lead to revenue and cos similar to how a human would by looking at the table of contents. Other times, while I did accept outputs, I made changes to the accepted output so I would understand what I have and can integrate it into the code well. Other times, even when I accepted outputs, I rewrote or adapted them so I could fully grasp the logic and ensure the code fit into how I want it.



