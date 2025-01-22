from django.urls import path, include
from calls.views import *


urlpatterns = [
    path("", HomePageView.as_view(), name="calls-home"),
    # path("compose-home", ComposeHome.as_view(), name="compose-home"),
    # path("author-lookup", AuthorLookup.as_view(), name="author-lookup"),
    # path("author-update/<int:pk>", AuthorUpdate.as_view(), name="author-update"),
    # path("journal-lookup", JournalLookup.as_view(), name="journal-lookup"),
    # path("journal-update/<int:pk>", JournalUpdate.as_view(), name="journal-update"),
    # path("article-lookup", ArticleLookup.as_view(), name="article-lookup"),
    # path("article-update/<int:pk>", ArticleUpdate.as_view(), name="article-update"),
    # path("summarize-articles", SummarizeArticles.as_view(), name="summarize-articles"),
]