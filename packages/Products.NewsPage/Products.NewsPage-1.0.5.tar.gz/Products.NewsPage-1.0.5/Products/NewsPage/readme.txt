Products.NewsPage is a simple product that enables displaying a
collection of news items in a folder default view, or by using the
macro in a custom page template.

The first 3 news items can be pinned by editing the NewsPage, and one
can also select which review state and paths to include/exclude.

To use the macro, try something like:

<metal:block tal:define="xyz python:request.set('newspage', context.newspage_object)">
  <span metal:use-macro="context/newspage_macros/macros/listing" />
</metal:block>
