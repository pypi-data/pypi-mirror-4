""" Init file for SRP

Context : SRP
Module  : SRP
Version : 1.1.2
Author  : Stefano Covino
Date    : 06/12/2012
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (28/09/2010) First named version.
        : (13/10/2010) V. 3.6.0.
        : (03/11/2010) V. 3.6.1beta.
        : (07/11/2010) V. 3.6.2beta and SRPPipelines.
        : (08/11/2010) V. 3.6.2. Conversion to int for TNG pipeline.
        : (17/11/2010) V. 3.7.0. SRP REM pipeline.
        : (03/12/2010) V. 3.7.1beta.
        : (12/12/2010) V. 3.7.1.
        : (14/12/2010) V. 3.7.2beta
        : (14/12/2010) V. 3.7.2.
        : (15/12/2010) V. 3.7.3beta.
        : (20/12/2010) V. 3.7.3.
        : (26/12/2010) V. 3.8.0beta.
        : (22/02/2011) V. 3.8.0.
        : (23/02/2011) V. 3.8.1beta.
        : (05/03/2011) V. 3.8.1.
        : (05/03/2011) V. 3.8.2beta.
        : (21/03/2011) V. 3.8.2.
        : (27/03/2011) V. 3.8.3beta.
        : (30/03/2011) V. 3.8.3.
        : (30/03/2011) V. 3.8.4beta.
        : (07/04/2011) V. 3.8.4.
        : (08/04/2011) V. 3.8.5beta.
        : (22/04/2011) V. 3.8.5.
        : (25/04/2011) V. 3.8.6beta.
        : (27/04/2011) V. 3.9.0beta.
        : (28/04/2011) V. 3.9.0.
        : (28/04/2011) V. 3.9.1beta.
        : (29/04/2011) V. 3.9.1.
        : (30/04/2011) V. 3.9.2beta.
        : (30/04/2011) V. 3.10.0beta.
        : (13/09/2011) V. 3.10.0.
        : (13/09/2011) V. 3.10.1b1.
        : (22/09/2011) V. 3.10.1b2 and no more SRPPipelines.
        : (29/09/2011) V. 3.10.1b3 and new filters.
        : (02/10/2011) V. 3.10.1b4, genera function for list of FITS files.
        : (11/10/2011) V. 3.10.1.
        : (12/10/2011) V. 3.10.2b1.
        : (23/10/2011) V. 3.10.2b2.
        : (30/10/2011) V. 3.10.2.
        : (03/11/2011) V. 3.10.3b1.
        : (04/11/2011) V. 3.10.3b2.
        : (15/11/2011) V. 3.10.3b3.
        : (10/12/2011) V. 3.10.3b4.
        : (16/12/2011) V. 3.10.3.
        : (12/01/2012) V. 3.10.4b1.
        : (12/01/2012) V. 3.10.4b2.
        : (04/02/2012) V. 3.10.4b3.
        : (08/02/2012) V. 3.10.4b4.
        : (14/02/2012) V. 3.10.4b5.
        : (18/02/2012) V. 3.10.4b6 and SRPSky.
        : (28/02/2012) V. 3.10.4.
        : (29/02/2012) V. 3.10.5b1.
        : (05/03/2012) V. 3.10.5b2.
        : (11/03/2012) V. 3.10.5b3.
        : (21/03/2012) V. 3.10.5b4.
        : (20/05/2012) V. 3.10.5b5.
        : (21/05/2012) V. 3.10.5.
        : (27/05/2012) V. 3.10.6b1.
        : (15/06/2012) V. 3.10.6b2.
        : (17/06/2012) V. 3.10.6b3.
        : (31/07/2012) V. 3.10.6b4.
        : (28/08/2012) V. 3.10.6.
        : (31/08/2012) V. 3.10.7b1.
        : (20/09/2012) V. 3.10.7b2.
        : (27/09/2012) V. 3.10.7b3 and SRPTime.
        : (04/12/2012) V. 3.10.7b4.
        : (06/12/2012) V. 3.10.7.
"""



# import
import pkg_resources


__all__ = ['SRPCatalogue', 'SRPFits', 'SRPFrames', 'SRPMath', 'SRPNet', 'SRPPhotometry', 
           'SRPPipelines', 'SRPPolarimetry', 'SRPREM', 'SRPSky', 'SRPSpectroscopy', 
           'SRPStatistics', 'SRPSystem', 'SRPTables', 'SRPTime', 'SRPTNG']


# Version
__version__ = '3.10.7'

