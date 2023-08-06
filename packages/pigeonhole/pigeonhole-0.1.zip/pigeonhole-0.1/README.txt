.. contents::

Introduction
============

Pigeonhole is a tool used to create dashboards from templates rendered with mr.bob:

    https://pypi.python.org/pypi/mr.bob

A complete example of using Pigeonhole is currently under development:

    https://github.com/maikroeder/encode.mouse

To get an idea of what kind of dashboards you will be able to produce with Pigeonhole, have 
a look at the ENCODE RNA Dashboards (human and mouse):

    http://genome.crg.es/encode_RNA_dashboard

Design
======

The post_render hook of mr.bob is used to get hold of the configuration for individual
mr.bob runs. This way, Pigeonhole does not need to know how mr.bob does its magic, and
can concentrate on plugging the individual templates together by calling them on demand
while rendering the dashboard.

Zope Page Template support for mr.bob
=====================================

Pigeonhole extends mr.bob with a renderer for Zope Page Templates, which can be 
used instead of the default Jinja2 templates: 

    https://pypi.python.org/pypi/zope.pagetemplate

To use this renderer, place the following line in your .mrbob.ini:

    [template]
    renderer = pigeonhole.rendering:pagetemplate_renderer