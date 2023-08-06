import copy
import simplejson as json

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError,  ObjectDoesNotExist
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

from geoprisma_config.models import *
from conf.types import *


class Command(BaseCommand):
    args = "<config.xml>"
    help = 'Import geoprisma xml config file'
    

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError('No xml config file provided')

        filename = args[0]

        self.rootElement = ElementTree()
        
        # do some checks
        try:
            self.rootElement.parse(filename)
        except IOError, e:
            print e
            raise CommandError('Unable to open %s' % filename)
        except ExpatError, e:
            print e
            raise CommandError('Unable to parse %s' % filename)

        if self.rootElement.getroot().tag != 'geoprisma':
            raise CommandError('%s is not a geoprisma xml config file' % filename)

        # registers
        # Used when parsing workspaces
        self.defaultMapContext = None
        self.defaultApplication = None
        # map contexts are read in parseWidgets(), but have to be added in the DB after resources
        self.mapContexts = []
        self.datastoreFields = {}

        # parse the entire config
        self.parseServices()
        self.parseDatastores()
        self.parseResources()
        self.parseFields()
        self.parseWidgets()
        self.parseMapContexts()
        self.parseApplications()
        self.parseSessions()

 
    def getNodeValue(self, element, tag):
        'Try to get a node value, return None if not found'

        node = element.find(tag)
        if node is None: return None

        return node.text
        
    def saveModel(self, model):
        'Clean model fields and save it in the database'

        try:
            model.full_clean() # validate the fields
            model.save()
        except ValidationError, e:
            for key, errors in e.message_dict.items():
                for error in errors: 
                    print "Error: field '%s' => %s" % (key, error)
            print "Error: Unable to save model '%s'" % model
            return 1
        except Exception, e:
            print e
            print "Error: Unable to save model '%s'" % model
            return 2

        return 0

    def generateJSON(self, elements):
        'Parse nodes and generate json'

        jsonDict = {}
        for element in elements:
            if len(element) is not 0:
                jsonDict[element.tag] = self.generateArray(element)
            else:
                jsonDict[element.tag] = element.text

        return jsonDict
        

    def generateArray(self, elements):
        
        array = []
        for element in elements:
            if len(element) is not 0:
                array.append(self.generateJSON(element))

        return array
                             

    def parseMapFishModel(self, values, elements):
        'Parse the <model> tag of the mapfish layer tree widget'

        for element in elements:
            newValues = copy.copy(values)
            resourceName = element.find('resourcename')
            if resourceName is not None:
                try :
                    resourceModel = Resource.objects.get(name=resourceName.text)
                    if resourceModel.resourceoption_set.filter(name='layertreepath').exists():
                        print "Unable to add layertreepath option in the resource  '%s': layertreepath already exists" % resourceName.text
                        continue
                    else:
                        resourceModel.resourceoption_set.create(name='layertreepath', value='/'.join(newValues))
                    if element.find('checked') is not None:
                        if resourceModel.resourceoption_set.filter(name='visibility').exists():
                            print "Unable to add visibility option in the resource  '%s': visibility already exists" % resourceName.text
                            continue
                        else:
                            resourceModel.resourceoption_set.create(name='visibility', value=element.find('checked').text)
                except ObjectDoesNotExist:
                    print "Unable to add layertreepath option in the resource  '%s': invalid resource" % resourceName.text
                    continue
            else:
                newValues.append(element.find('textkey').text)
                self.parseMapFishModel(newValues, element.find('children'))

    def parseServices(self):
        'Parse services in the xml config and add them in the database'

        services = self.rootElement.find('services')
        if services is None or len(services.getchildren()) == 0:
            print 'No services found'
            return

        count = 0
        for service in services.getchildren():
            # verify that the type is valid
            type = None
            for t in SERVICE_TYPES:
                if t[1].lower() == service.tag:
                    type = t[0]
                    break
                
            if type is None:
                print "Skipping service '%s': invalid type" % service.tag
                continue
            
            # create the service model and save it
            serviceModel = Service()
            serviceModel.type = type
            serviceModel.name = self.getNodeValue(service, 'name')
            serviceModel.source = self.getNodeValue(service, 'source')
            if self.saveModel(serviceModel) is 0:
                
                # TODO parse service options, not currently supported in xml config (only provider ...)
                provider = service.find('provider')
                if provider is not None:
                    serviceModel.serviceoption_set.create(name=provider.tag, value=provider.text)

                count += 1;


        print "Imported %d service(s)" % count
            

    def parseDatastores(self):
        'Parse datastores in the xml config and add them in the database'
        
        datastores = self.rootElement.find('datastores')
        if datastores is None or len(datastores.getchildren()) == 0:
            print 'No datastores found'
            return

        count = 0
        for datastore in datastores.findall('datastore'):
            
            datastoreModel = Datastore()
            datastoreModel.name = self.getNodeValue(datastore, 'name')
            datastoreOptions = []

            # Verify that the service exists
            try:
                serviceModel = Service.objects.get(name=self.getNodeValue(datastore, 'service'))
                datastoreModel.service = serviceModel
            except ObjectDoesNotExist:
                print "Skipping datastore '%s': invalid service" % datastoreModel.name
                continue

            # iterate the params
            params = datastore.find('params')
            if params is not None:
                for param in params.getchildren():
                    # if the param is a container... ignore it.
                    if len(param) is not 0 and param.tag != 'fields':
                        print "Ignoring param '%s': it's a container" % param.tag
                    elif param.tag == 'layers':
                        datastoreModel.layers = param.text
                    else:
                        # Add a datastore options
                        datastoreOption = DatastoreOption(name=param.tag, 
                                                          value=param.text)
                        datastoreOptions.append(datastoreOption)
                        
            if self.saveModel(datastoreModel) is 0:
                for datastoreOption in datastoreOptions:
                    datastoreOption.datastore = datastoreModel
                    self.saveModel(datastoreOption)

                count += 1;

            # parse fields
            if params is not None:
                fields =  params.find('fields')
                if fields is not None:
                    self.datastoreFields[datastoreModel] = fields            

        print "Imported %d datastore(s)" % count


    def parseWidgets(self):
        'Parse widgets in the xml config and add them in the database'
        
        widgets = self.rootElement.find('widgets')
        if widgets is None or len(widgets.getchildren()) == 0:
            print 'No widgets found'
            return

        count = 0
        for widget in widgets.getchildren():

            if widget.tag == 'map':
                # register the map context, will be parsed after the resources
                self.mapContexts.append(widget);
                continue

            # verify that the type is valid
            type = None
            for t in WIDGET_TYPES:
                if t[1].lower() == widget.tag:
                    type = t[0]
                    break
                
            if type is None:
                print "Skipping widget '%s': invalid type" % widget.tag
                continue

            widgetModel = Widget()
            widgetModel.type = type
            widgetModel.name = self.getNodeValue(widget, 'name')

            if self.saveModel(widgetModel) is 0:
                # iterate the options
                options = widget.find('options')
                if options:
                    for option in options.getchildren():

                        if option.tag == 'model':
                            self.parseMapFishModel([], option)
                        else:
                            # if the option is a container.. check the suboptions
                            if len(option) is not 0:
                                jsonValue = []
                                for suboption in option:
                                    if len(suboption) is not 0:
                                        # another container ? generate json
                                        jsonValue.append(self.generateJSON(suboption))
                                    else:
                                        widgetModel.widgetoption_set.create(name=suboption.tag, value=suboption.text)                                

                                if jsonValue:
                                    widgetModel.widgetoption_set.create(name=option.tag, value=json.dumps(jsonValue))

                            else:
                                # Add a widget options
                                widgetModel.widgetoption_set.create(name=option.tag, value=option.text)
            
                # fix all GeoExtToolbar "widget" options
                geoExtToolbarWidgets = Widget.objects.filter(type=22)
                for geoExtToolbarWidget in geoExtToolbarWidgets:
                    # get the widget options
                    widgetOptions = geoExtToolbarWidget.widgetoption_set.filter(name='widget')
                    for widgetOption in widgetOptions:
                        try:
                            widgetModel = Widget.objects.get(name=widgetOption.value)
                            widgetOption.value = widgetModel.id
                            self.saveModel(widgetOption)
                        except ObjectDoesNotExist:
                            continue

                # fix all QueryOnClick "result" and "featurepanel" options
                queryOnClickWidgets = Widget.objects.filter(type=7)
                for queryOnClickWidget in queryOnClickWidgets:
                    # get the options
                    widgetOptions = queryOnClickWidget.widgetoption_set.filter(name__in=['result','featurepanel', 'RESULT', 'FEATUREPANEL'])
                    for widgetOption in widgetOptions:
                        try:
                            widgetModel = Widget.objects.get(name=widgetOption.value)
                            widgetOption.value = widgetModel.id
                            self.saveModel(widgetOption)
                        except ObjectDoesNotExist:
                            continue

                count += 1;

        print "Imported %d widget(s)" % count


    def parseResources(self):
        'Parse resources in the xml config and add them in the database'
        
        resources = self.rootElement.find('resources')
        if resources is None or len(resources.getchildren()) == 0:
            print 'No resources found'
            return

        count = 0
        for resource in resources.findall('resource'):
            
            resourceModel = Resource()
            resourceModel.name = self.getNodeValue(resource, 'name')
            resourceModel.aclName = resourceModel.name
            resourceDatastores = []

            datastores = resource.find('datastores')
            if datastores is None or len(datastores.findall('datastore')) == 0:
                print "Skipping resource '%s': no datastores associated" % resourceModel.name
                continue

            for datastore in datastores.findall('datastore'):
                # Verify that the datastore exists
                try:
                    datastoreModel = Datastore.objects.get(name=datastore.text)
                    resourceDatastores.append(datastoreModel)
                except ObjectDoesNotExist:
                    print "Failed to link to datastore '%s': invalid datastore" % datastore.text
                    continue

            # do not save it there is no valid datastores
            if not resourceDatastores:
                print "Skipping resource '%s': no datastores associated" % resourceModel.name
                continue

            
            if self.saveModel(resourceModel) is not 0:
                continue

            for resourceDatastore in resourceDatastores:
                resourceModel.datastores.add(resourceDatastore)

            # iterate the options
            options = resource.find('options')
            if options is not None:
                for option in options.getchildren():
                    if option.tag == 'title':
                        resourceModel.resourceoption_set.create(name=option.tag, 
                                                                value=option.text,
                                                                key=self.getNodeValue(option, 'key'),
                                                                domain=self.getNodeValue(option, 'domain'))
                    # if the option is a container... ignore it.
                    elif len(option) is not 0:
                        print "Ignoring option '%s': it's a container" % option.tag
                    else:
                        # Add a resource options
                        resourceModel.resourceoption_set.create(name=option.tag, value=option.text)

            count += 1;

        print "Imported %d resource(s)" % count


    def parseFields(self):
        'Parse datastore fields and add them in the database'

        if self.datastoreFields is {}:
            print "No fields found"
            return

        for datastoreModel, fields in self.datastoreFields.items():
            for field in fields.findall('field'):
                fieldModel = Field()
                fieldOptions = {}
                for option in field.getchildren():
                    if option.tag == 'name':
                        fieldModel.name = option.text
                    elif option.tag == 'text':
                        fieldModel.title = option.text
                    else:
                        fieldOptions[option.tag] = option.text
                        
                        # try to save the field if it doesn't exist
                        if Field.objects.filter(name=fieldModel.name).exists():
                            fieldModel = Field.objects.get(name=fieldModel.name)
                        elif self.saveModel(fieldModel) is not 0:
                            continue

                        # add the field options
                        for key,value in fieldOptions.items():
                            fieldOptionModel = FieldOption(name=key, value=value)
                            fieldModel.fieldoption_set.add(fieldOptionModel)
                            
                        # Iterate the resources that are linked to that datastore 
                        resourceSet = datastoreModel.resource_set.all()
                        for resource in resourceSet:
                            resource.resourcefield_set.create(field=fieldModel)


    def parseMapContexts(self):
        'Parse map contexts in the xml config and add them in the database'

        if not self.mapContexts:
            print "No map contexts found"
            return

        count = 0
        for mapContext in self.mapContexts:
            
            mapContextModel = MapContext()
            mapContextModel.name = self.getNodeValue(mapContext, 'name')
            
            if self.saveModel(mapContextModel) is not 0:
                continue # unable to save model... 

            # iterate the options
            options = mapContext.find('options')
            if options is not None:
                for option in options.getchildren():
                    if len(option) is not 0:
                        print "Ignoring option '%s': it's a container" % option.tag
                    else:
                        # Add a map context options
                        mapContextModel.mapcontextoption_set.create(name=option.tag, 
                                                                    value=option.text)

            # iterate the layers
            layers = mapContext.find('layers')
            if layers is not None:
                for layer in layers.findall('layer'):

                    resources = layer.find('resourcenames')
                    if resources is None or len(resources.getchildren()) == 0:
                        continue # no resourcenames ?
                    else:
                        # first, read the layer options
                        layerOptions = []
                        options = layer.find('options')
                        if options is not None and len(options.getchildren()) != 0:
                            for option in options.getchildren():
                                if len(option) is not 0:
                                    print "Ignoring option '%s': it's a container" % option.tag
                                else:
                                    layerOptions.append(option)

                        for resource in resources.findall('resourcename'):
                            # verify that the resource exists
                            try:
                                resourceModel = Resource.objects.get(name=resource.text)
                                resourceModel.resource = resourceModel
                                # Write the layer options in the resource
                                for layerOption in layerOptions:
                                    if not resourceModel.resourceoption_set.filter(name=layerOption.tag).exists():
                                        resourceModel.resourceoption_set.create(name=layerOption.tag, value=layerOption.text)

                                # Add a map context resource
                                mapContextModel.mapcontextresource_set.create(resource=resourceModel)
                            except ObjectDoesNotExist:
                                print "Failed to link to resource '%s': invalid resource" % resource.text
                                continue
                        
            if count == 0:
                self.defaultMapContext = mapContextModel
            count += 1;
                        
        print "Imported %d map context(s)" % count

    def parseApplications(self):
        'Parse applications in the xml config and add them in the database'
    
        applications = self.rootElement.find('layouts')
        if applications is None or len(applications.getchildren()) == 0:
            print 'No applications found'
            return

        count = 0
        for application in applications.findall('layout'):

            drawMode = self.getNodeValue(application, 'drawmode')
            # verify that the type is valid
            type = None
            for t in APPLICATION_TYPES:
                if t[1].lower() == drawMode:
                    type = t[0]
                    break
                
            if type is None:
                print "Skipping application '%s': invalid type" % drawMode
                continue

            applicationModel = Application()
            applicationModel.name = self.getNodeValue(application, 'name')
            applicationModel.type = type
            applicationModel.template = self.getNodeValue(application, 'file')

            if self.saveModel(applicationModel) is 0:
                if count == 0:
                    self.defaultApplication = applicationModel
                count += 1
            
        print "Imported %d application(s)" % count


    def parseSessions(self):
        'Parse sessions in the xml config and add them in the database'

        sessions = self.rootElement.find('workspaces')
        if sessions is None or len(sessions.getchildren()) == 0:
            print 'No sessions found'
            return

        count = 0
        for session in sessions.findall('workspace'):

            name = self.getNodeValue(session, 'name')
            application = self.getNodeValue(session, 'layout')
            if application is None and self.defaultApplication is not None:
                application = self.defaultApplication.name

            if application is None:
                print "Skipping session '%s': invalid application or map context" % name
                continue

            sessionModel = Session()
            sessionModel.name = name

            mapContextModel = MapContext()
            mapContextModel.name = name

            if self.saveModel(mapContextModel) is not 0:
                continue # unable to save model... 

            try:
                sessionModel.application = Application.objects.get(name=application)
                sessionModel.mapContext = mapContextModel
            except ObjectDoesNotExist:
                print "Failed to link to application '%s': invalid application" % application
                continue
                
            if self.saveModel(sessionModel) is 0:
                count += 1

            
            resources = session.find('resources')
            for resource in resources.findall('resource'):
                name = self.getNodeValue(resource, 'name')
                if name is None:
                    print "Failed to link to resource '%s': invalid resource" % name
                    continue

                try:
                    resourceModel = Resource.objects.get(name=name)
                    if not sessionModel.mapContext.mapcontextresource_set.filter(resource=resourceModel).exists():
                        sessionModel.mapContext.mapcontextresource_set.create(resource=resourceModel)
                    
                except ObjectDoesNotExist:
                    print "Failed to link to resource '%s': invalid resource" % name
                    continue

                widgets = resource.find('widgets')
                for widget in widgets.findall('widget'):
                    if len(widget.getchildren()) != 0:
                        name = self.getNodeValue(widget, 'name')
                        if name is None:
                            print "Failed to link to widget '%s': invalid widget" % name
                            continue

                        try:
                            widgetModel = Widget.objects.get(name=name)
                            if not sessionModel.application.applicationwidget_set.filter(widget=widgetModel).exists():
                                sessionModel.application.applicationwidget_set.create(widget=widgetModel)
                        except ObjectDoesNotExist:
                            print "Failed to link to widget '%s': invalid widget" % name
                            continue

                    else:
                        try:
                            widgetModel = Widget.objects.get(name=widget.text)
                            if not sessionModel.application.applicationwidget_set.filter(widget=widgetModel).exists():

                                sessionModel.application.applicationwidget_set.create(widget=widgetModel)
                        except ObjectDoesNotExist:
                            print "Failed to link to widget '%s': invalid widget" % widget.text
                            continue

        print "Imported %d session(s)" % count


    def parseSessionsOld(self):
        'Parse sessions in the xml config and add them in the database'

        sessions = self.rootElement.find('workspaces')
        if sessions is None or len(sessions.getchildren()) == 0:
            print 'No sessions found'
            return

        count = 0
        for session in sessions.findall('workspace'):

            name = self.getNodeValue(session, 'name')
            application = self.getNodeValue(session, 'layout')
            if application is None and self.defaultApplication is not None:
                application = self.defaultApplication.name

            mapContext = self.getNodeValue(session, 'map')
            if  mapContext is None and self.defaultMapContext is not None:
                mapContext = self.defaultMapContext.name

            if application is None or mapContext is None:
                print "Skipping session '%s': invalid application or map context" % name
                continue

            sessionModel = Session()
            sessionModel.name = name

            try:
                sessionModel.application = Application.objects.get(name=application)
            except ObjectDoesNotExist:
                print "Failed to link to application '%s': invalid application" % application
                continue
                
            try:
                sessionModel.mapContext = MapContext.objects.get(name=mapContext)
            except ObjectDoesNotExist:
                print "Failed to link to map context '%s': invalid map context" % mapContext
                continue

            if self.saveModel(sessionModel) is 0:
                count += 1

            
            resources = session.find('resources')
            for resource in resources.findall('resource'):
                name = self.getNodeValue(resource, 'name')
                if name is None:
                    print "Failed to link to resource '%s': invalid resource" % name
                    continue

                try:
                    resourceModel = Resource.objects.get(name=name)
                    if not sessionModel.mapContext.mapcontextresource_set.filter(resource=resourceModel).exists():
                        sessionModel.mapContext.mapcontextresource_set.create(resource=resourceModel)
                    
                except ObjectDoesNotExist:
                    print "Failed to link to resource '%s': invalid resource" % name
                    continue

                widgets = resource.find('widgets')
                for widget in widgets.findall('widget'):
                    if len(widget.getchildren()) != 0:
                        name = self.getNodeValue(widget, 'name')
                        if name is None:
                            print "Failed to link to widget '%s': invalid widget" % name
                            continue

                        try:
                            widgetModel = Widget.objects.get(name=name)
                            if not sessionModel.application.applicationwidget_set.filter(widget=widgetModel).exists():
                                sessionModel.application.applicationwidget_set.create(widget=widgetModel)
                        except ObjectDoesNotExist:
                            print "Failed to link to widget '%s': invalid widget" % name
                            continue

                    else:
                        try:
                            widgetModel = Widget.objects.get(name=widget.text)
                            if not sessionModel.application.applicationwidget_set.filter(widget=widgetModel).exists():

                                sessionModel.application.applicationwidget_set.create(widget=widgetModel)
                        except ObjectDoesNotExist:
                            print "Failed to link to widget '%s': invalid widget" % widget.text
                            continue

        print "Imported %d session(s)" % count
