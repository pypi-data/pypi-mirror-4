# GeoPrisma constants

APPLICATION_TYPES = (
    (1, 'ExtJS'),
)

WIDGET_TYPES = (
    #    1 => 'quickzoom', // removed
#    (2, 'Map'),  do not use this in django.
    (3, 'MapFishLayerTree'),
    (4, 'MapFishRecenter'),
    (5, 'MeasureTool'),
    #         6 => 'toolbar', // removed
    (7, 'QueryonClick'),
    #         8 => 'Popup', // removed
    (9, 'ResulTextGrid'),
    #         10 => 'removed',
    (11, 'InitialView'),
    (12, 'ZoomSlider'),
    (13, 'MousePosition'),
    (14, 'GetMousePosition'),
    (15, 'Scale'),
    (16, 'EditFeature_Create'),
    (17, 'EditFeature_Update'),
    (18, 'EditFeature_Delete'),
    #(19, 'FeaturePanel_Form'), # will not be supported by db driver
    (20, 'FeaturePanel_Selector'),
    #(21, 'LegendPanel'), # removed
    (22, 'GeoExtToolbar'),
    #(23, 'Merge'), # removed
    #(24, 'Split'), # removed
    (25, 'Shortcut'),
    #(26, 'GeoExtUx_GeoNamesSearchCombo'), # currently not supported by db driver
    (27, 'GeoExtUx_Redliningpanel'),
    (28, 'PdfPrint'),
    (29, 'WMSLayerAdder'),
    (30, 'GeoExtUx_ShortcutCombo'),
    (31, 'GeoExtUx_ZoomTo'),
    (32, 'HTWindow'),
    (33, 'UnselectAll'),
    (34, 'GeoExtPrintForm'),
    (35, 'FileTreePanel'),
    (36, 'GeoExtUx_LayerTreeBuilder'),
    #(37, 'MapPanel'), # don't use it in django
    #(38, 'Layer') # don't use it in django
    (39, 'QueryByRect'),
    (40, 'FeaturePanel_AttributeForm'),
    (41, 'FeaturePanel_CustomForm'),
    (42, 'GeoExtUx_WMSBrowser'),
    (43, 'VectorLayer'),
    (44, 'ResultVectorLayer'),
    (45, 'QueryOnClickWizard'),
    (46, 'GeoExtUx_PrintPreview'),
    (47, 'WFSFilterBuilder'),
    (48, 'TemplatePopup'),
    (49, 'Toggle'),
    (50, 'EditFeature_Split'),
    (51, 'EditFeature_Drag'),
    (52, 'EditFeature_Copy'),
    (53, 'EditFeature_Confirm'),
    (54, 'KeepActiveSession'),
    # for user-defined widgets use numbers grater than 9999 ??
    (10001, 'DXFImport'), 
    (10002, 'GeoctopusPrint'), 
    (10003, 'GeoctopusSplitter')
    )


SERVICE_TYPES = (
    (1, 'WMS'),
    (2, 'TileCache'),
    (3, 'FeatureServer'),
    (4, 'GYMO'),
    #(5, 'Widget'), # deprecated
    #(6, 'MapServer'), # deprecated
    (7, 'MapFishPrint'),
    (8, 'File'),
    (9, 'WFS'),
    (10, 'HttpRequest')
    )

