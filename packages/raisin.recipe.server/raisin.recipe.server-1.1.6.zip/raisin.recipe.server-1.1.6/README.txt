====================
raisin.recipe.server
====================
------------------------
Configure Raisin servers
------------------------

**raisin.recipe.server** configures Raisin servers

Background
==========

The Raisin project provides web servers for the Grape (Grape RNA-Seq Analysis Pipeline
Environment). Grape is a pipeline for processing and analyzing RNA-Seq data developed at 
the Bioinformatics and Genomics unit of the Centre for Genomic Regulation (CRG) in 
Barcelona. 

Important Note
==============

The raisin.recipe.server package is a Buildout recipe used by Grape, and is not
a standalone Python package. It is only going to be useful as installed by the 
grape.buildout package.

To learn more about Grape, and to download and install it, go to the Bioinformatics 
and Genomics website at:

http://big.crg.cat/services/grape

Motivation
==========

The Raisin web server needs to be easily deployed for development and in production.
The Pyramid web server, the restish Restful server, and supervisord are fully 
configured.

Here at the CRG, we need web servers for our RNASeq pipelines per project, but also
for a number of projects together. A server may be used by one researcher, internally 
for a group of researchers, or on the Internet for sharing with a research community.

Installation
============

The grape.recipe.server package is already installed by grape.buildout, so
you don't have to do this. 

Configuration
=============

The buildout part that configures the raisin.recipe.server does not currently need
any configuration. This is all the server part defines:

[server]
recipe = raisin.recipe.server
