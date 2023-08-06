= raisin.pyramid =

This is a Pyramid server that is part of Raisin, the web application used for publishing
the summary statistics of Grape, a pipeline used for processing and analyzing RNA-Seq
data."""

= About the server =

The purpose of this module is to configure the pages of the project so that the
Pyramid application knows them and can serve them using the right models.

The configuration of the pages and boxes is imported from raisin.box and raisin.page:

    from raisin.page import PAGES
    from raisin.box import BOXES

The models are imported from raisin.restyler:

    from raisin.restyler.page import Page
    from raisin.restyler.box import Box

See the respective packages to learn about how to customize the pages and boxes.

All you need to know is that Pyramid is able to render all pages, and also renders all
boxes that appear in the pages individually, and in different formats. The Pyramid
server does not know about these formats, it just configures routes to them.
