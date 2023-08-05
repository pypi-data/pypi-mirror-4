=========
Autograde
=========

Required Settings
=================

AUTOGRADE_PROJECT_UPLOAD_PATH
-----------------------------
Upload directory for files (example: os.path.join(MEDIA_ROOT, 'projects/')).

AUTOGRADE_ZIP_TMP
-----------------
Temporary location for project zips to be stored (example: MEDIA_ROOT).

Optional Settings
=================

AUTOGRADE_PROJECT_META_MODEL
----------------------------
Model to be used to store project meta data. Default: "autograde.ProjectMeta". 
