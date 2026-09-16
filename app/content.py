from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    title: str
    body: str


PROMOTIONS = (
    Item("Featured Promotion", "A featured promotion can be presented here with its offer, eligibility, validity period and key terms. Users can read the complete details in Telegram."),
    Item("Campaign Information", "Use this section for a current campaign summary, including what is offered, who it is for and any important conditions."),
    Item("Promotion Guidelines", "Submitted promotions should be clear, accurate and relevant. Do not include passwords, payment credentials or other private information."),
)

UPDATES = (
    Item("Latest Starz Update", "Starz Promosyon keeps its core promotion information and updates available directly inside the bot."),
    Item("In-App Experience", "Users can browse information, read updates and submit promotion text without being sent to an external website."),
    Item("Submission Status", "Submitted promotion text is validated, saved locally and assigned a reference number so the submission can be identified later."),
)
