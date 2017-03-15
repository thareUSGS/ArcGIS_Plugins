## CTX_CreateMosaic_fromASUgeoTiff.pyt
==============

New version which creates a CTX Mosaic from new 2017 ASU GeoTiffs. Optionally creates a ArcMap mosaic data type from downloaded images using Equidistant Cylindrical clon=0. By default the edges are trimmed by 100 meters in the mosaic but this can be set to 0 since GeoTiff are lossless. Uses Footprints from GeoScience Node: http://ode.rsl.wustl.edu/mars/datafile/derived_products/coverageshapefiles/mars/mro/ctx/edr/mars_mro_ctx_edr_c0a.zip

==============

Both CTX_CreateMosaic_fromASU.pyt and CTX_CreateMosaic_fromASUgeoJp2.pyt are __now deprecated__. ASU no longer supports Jpeg2000 files for CTX. They have changed to a compressed GeoTiff with pyramids.

CTX_CreateMosaic_fromASU.pyt
* OLD -- original version which creates a CTX mosaic using ASU's CTX jp2s and isis header. It requires a step to attached the isis header to the jp2 making a geojp2.

CTX_CreateMosaic_fromASUgeoJp2.pyt
* OLD -- version which creates a CTX Mosaic from new 2015 ASU GeoJpeg2000. Optionally creates a ArcMap mosaic data type from downloaded images using Equidistant Cylindrical clon=0. No needed for ISIS headers anymore since ASU supports GeoJpeg2000 images now. Uses Footprints from GeoScience Node: http://ode.rsl.wustl.edu/mars/datafile/derived_products/coverageshapefiles/mars/mro/ctx/edr/mars_mro_ctx_edr_c0a.zip

support email: thare@usgs.gov

