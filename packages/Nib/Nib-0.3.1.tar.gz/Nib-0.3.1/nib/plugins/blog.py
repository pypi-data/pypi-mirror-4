import datetime
import re
from nib import Document, Processor, before, document

dateregex = re.compile(r'(?P<year>\d\d\d\d)[-./](?P<month>\d\d)[-./](?P<day>\d\d)')

@before
class BlogDateProcessor(Processor):
    def document(self, document):
        if 'date' in document:
            if document.group is None:
                document.group = 'blog'

        return document

@document('blog')
class BlogDocumentProcessor(Processor):
    def process(self, documents, resources):
        uris = self.options['blog']['uris']
        templates = self.options['blog']['templates']
        blog_pages = {}

        def blog_page(name, parent=None, child=None, **kwargs):
            path = uris[name].format(**kwargs)

            if path not in blog_pages:
                page = Document(path=path,
                                content='',
                                short='',
                                template=templates[name],
                                pages=[],
                                )
                if parent:
                    parent['pages'].append(page)
                blog_pages[path] = page
            else:
                page = blog_pages[path]

            if child:
                page['pages'].append(child)

            return page

        feed_page = blog_page('feed')
        index_page = blog_page('index')
        archive_page = blog_page('archive')
        tags_page = blog_page('tags')

        for document in documents:
            if type(document['date']) == datetime.date:
                date = document['date']
                date = {
                    'year': date.year,
                    'month': date.month,
                    'day': date.day,
                }

                blog_page('yearly', parent=archive_page, child=document, **date)
                blog_page('monthly', parent=archive_page, child=document, **date)
                blog_page('daily', parent=archive_page, child=document, **date)

            if 'tags' in document:
                tags = [token.strip() for token in document['tags'].split(',')]
                for tag in tags:
                    blog_page('tag', parent=tags_page, child=document, tag=tag)

            feed_page['pages'].append(document)
            index_page['pages'].append(document)

        documents.extend(blog_pages.values())

        return documents, resources
