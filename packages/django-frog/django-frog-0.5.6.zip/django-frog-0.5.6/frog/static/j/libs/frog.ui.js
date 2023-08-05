// Frog UI

Frog.UI = (function(Frog) {
    var ID, Store, ToolBar;
    var navmenu = Ext.create('Ext.menu.Menu');


    // -- Models
    Ext.define('Gallery', {
        extend: 'Ext.data.Model',
        fields: [
            {name: 'id'},
            {name: 'title'},
            {name: 'image_count', type: 'int'},
            {name: 'video_count', type: 'int'},
            {name: 'owner'},
            {name: 'description'},
            {name: 'private'}
        ]
    });
    Store = Ext.create('Ext.data.Store', {
        autoLoad: true,
        autoSync: true,
        model: 'Gallery',
        proxy: {
            type: 'ajax',
            url: '/frog/gallery',
            reader: {
                type: 'json',
                root: 'values'
            }
        }
    });

    ToolBar = Ext.create('Ext.toolbar.Toolbar');
    RemoveObserver = new Frog.Observer();
    ChangeObserver = new Frog.Observer();

    function setId(id) {
        ID = id;
    }

    function render(el) {
        var managemenu, menuremove, menucopy, menudownload, menuswitchartist;
        ToolBar.render(el);
        // -- Navigation panel
        navmenu.add(buildNav());
        ToolBar.add({
            text: 'Navigation',
            icon: FrogStaticRoot + '/frog/i/compass.png',
            menu: navmenu
        });
        // -- Upload button
        ToolBar.add({
            id: 'frogBrowseButton',
            text: 'Upload',
            icon: FrogStaticRoot + '/frog/i/add.png'
        });
        // -- Edit Tags button
        ToolBar.add({
            text: 'Edit Tags',
            icon: FrogStaticRoot + '/frog/i/tag_orange.png',
            handler: editTagsHandler
        });
        // Manage Menu
        menuremove = Ext.create('Ext.menu.Item', {
            text: 'Remove Selected',
            icon: FrogStaticRoot + '/frog/i/cross.png',
            handler: removeHandler
        });
        menucopy = Ext.create('Ext.menu.Item', {
            text: 'Copy to Gallery',
            icon: FrogStaticRoot + '/frog/i/page_white_copy.png',
            handler: copyHandler
        });
        menudownload = Ext.create('Ext.menu.Item', {
            text: 'Download Sources',
            icon: FrogStaticRoot + '/frog/i/compress.png',
            handler: downloadHandler
        });
        menuswitchartist = Ext.create('Ext.menu.Item', {
            text: 'Switch Artist',
            icon: FrogStaticRoot + '/frog/i/user_edit.png',
            handler: switchArtistHandler
        });
        managemenu = Ext.create('Ext.menu.Menu', {
            items: [menuremove, menucopy, menudownload, '-', menuswitchartist]
        });
        ToolBar.add({
            text: 'Manage',
            icon: FrogStaticRoot + '/frog/i/photos.png',
            menu: managemenu
        });
        ToolBar.add('-')
        // -- RSS button
        ToolBar.add({
            icon: FrogStaticRoot + '/frog/i/feed.png',
            handler: rssHandler
        });
        // -- Help button
        ToolBar.add({
            icon: FrogStaticRoot + '/frog/i/help.png',
            handler: helpHandler
        });
        // -- Preferences Menu
        ToolBar.add({
            icon: FrogStaticRoot + '/frog/i/cog.png',
            menu: buildPrefMenu()
        });
    }
    function addEvent(event, fn) {
        switch(event) {
            case 'remove':
                RemoveObserver.subscribe(fn);
                break;
            case 'change':
                ChangeObserver.subscribe(fn);
                break;
        }
    }
    function addTool(label, icon, callback) {
        ToolBar.add({
            text: label,
            icon: icon,
            handler: callback
        });
    }


    // Private
    function buildNav() {
        var grid = Ext.create('Ext.grid.Panel', {
            width: 600,
            height: 300,
            frame: true,
            title: 'Galleries',
            store: Store,
            columns: [{
                text: 'Title',
                flex: 2,
                sortable: true,
                dataIndex: 'title'
            }, {
                text: 'Images',
                flex: 1,
                sortable: true,
                dataIndex: 'image_count',
                field: {
                    xtype: 'textfield'
                }
            }, {
                text: 'Videos',
                flex: 1,
                sortable: true,
                dataIndex: 'video_count',
                field: {
                    xtype: 'textfield'
                }
            }, {
                text: 'Private',
                flex: 1,
                dataIndex: 'private'
            }, {
                text: 'Description',
                flex: 2,
                dataIndex: 'description'
            }]
        });
        grid.on('itemClick', function(view, rec, item) {
            location.href = '/frog/gallery/' + rec.data.id;
        });

        return grid;
    }
    function buildPrefMenu() {
        var colorMenu = Ext.create('Ext.menu.ColorPicker', {
            height: 24,
            handler: function(cm, color){
                Frog.Prefs.set('backgroundColor', JSON.stringify('#' + color));
            }
        });
        colorMenu.picker.colors = ['000000', '424242', '999999', 'FFFFFF'];
        var tileSizeHandler = function(item, checked) {
            var size = item.value;
            Frog.Prefs.set('tileCount', size);
            item.parentMenu.hide();
            ChangeObserver.fire(Frog.Prefs);
        }
        var batchSize = Ext.create('Ext.form.field.Number', {
            value: Frog.Prefs.batchSize,
            minValue: 0,
            maxValue: 500
        });
        batchSize.on('change', function(field, val) { 
            Frog.Prefs.set('batchSize', val);
        });

        var menu = Ext.create('Ext.menu.Menu', {
            items: [
                {
                    text: 'Viewer Background',
                    menu: colorMenu
                },
                {
                    text: 'Thumbnail Size',
                    menu: [
                        {
                            text: 'Large (6)',
                            value: 6,
                            checked: Frog.Prefs.tileCount === 6,
                            group: 'theme',
                            checkHandler: tileSizeHandler
                        }, {
                            text: 'Medium (9)',
                            value: 9,
                            checked: Frog.Prefs.tileCount === 9,
                            group: 'theme',
                            checkHandler: tileSizeHandler
                        }, {
                            text: 'Small (12)',
                            value: 12,
                            checked: Frog.Prefs.tileCount === 12,
                            group: 'theme',
                            checkHandler: tileSizeHandler
                        }
                    ]
                },
                {
                    text: 'Item Request Size',
                    menu: [
                        batchSize
                    ]
                }, {
                    xtype: 'menucheckitem',
                    text: 'Include Images',
                    checked: Frog.Prefs.include_image,
                    checkHandler: function(item, checked) {
                        Frog.Prefs.set('include_image', checked);
                        item.parentMenu.hide();
                        ChangeObserver.fire(Frog.Prefs);;
                    }
                }, {
                    xtype: 'menucheckitem',
                    text: 'Incude Video',
                    checked: Frog.Prefs.include_video,
                    checkHandler: function(item, checked) {
                        Frog.Prefs.set('include_video', checked);
                        item.parentMenu.hide();
                        ChangeObserver.fire(Frog.Prefs);;
                    }
                }
                
            ]
        });

        return menu;
    }
    function editTagsHandler() {
        var guids = [];
        $$('.selected').each(function(item) {
            guids.push(item.dataset.frog_guid);
        });
        var win = Ext.create('widget.window', {
            title: 'Edit Tags',
            icon: FrogStaticRoot + '/frog/i/tag_orange.png',
            closable: true,
            resizable: false,
            modal: true,
            width: 800,
            height: 600,
            layout: 'fit',
            bodyStyle: 'padding: 5px;',
            items: [{
                loader: {
                    url: '/frog/tag/manage?guids=' + guids.join(','),
                    contentType: 'html',
                    loadMask: true,
                    autoLoad: true,
                    scripts: true,
                    cache: false
                }
            }],
            buttons: [{
                text: 'Save',
                handler: function() {
                    var add = [], rem = [];
                    $$('#frog_add li').each(function(item) {
                        var id = item.dataset.frog_tag_id;
                        add.push(id);
                    });
                    $$('#frog_rem li').each(function(item) {
                        var id = item.dataset.frog_tag_id;
                        rem.push(id);
                    });
                    
                    new Request.JSON({
                        url: '/frog/tag/manage',
                        headers: {"X-CSRFToken": Cookie.read('csrftoken')},
                        onSuccess: function() {
                            add.each(function(tag) {
                                Frog.Tags.get(tag);
                            });
                        }
                    }).POST({
                        add: add.join(','),
                        rem: rem.join(','),
                        guids: guids.join(',')
                    });
                    win.close();
                }
            },{
                text: 'Cancel',
                handler: function() {
                    win.close();
                }
            }]
        });
        win.show();
    }
    function removeHandler() {
        var ids = [];
        $$('.selected').each(function(item) {
            ids.push(item.dataset.frog_tn_id.toInt());
        });
        RemoveObserver.fire(ids);
    }
    function copyHandler() {
        var win = Ext.create('widget.window', {
            title: 'Copy to Gallery',
            icon: FrogStaticRoot + '/frog/i/page_white_copy.png',
            closable: true,
            resizable: false,
            modal: true,
            width: 600,
            height: 300,
            bodyStyle: 'padding: 5px;'
        });
        win.show();

        var fp = Ext.create('Ext.FormPanel', {
            items: [{
                xtype: 'label',
                text: "Copy images to a new Gallery:"
            }, {
                xtype:'fieldset',
                title: 'New Gallery',
                items: [
                    {
                        fieldLabel: 'Title',
                        xtype: 'textfield',
                        name: 'title'

                    }, {
                        fieldLabel: 'Description',
                        xtype: 'textfield',
                        name: 'description'
                    }, {
                        fieldLabel: 'Private?',
                        xtype: 'checkbox',
                        name: 'private'
                    }
                ]
            }, {
                xtype: 'label',
                text: 'Or choose an existing one:'
            }, {
                xtype:'fieldset',
                title: 'Existing Gallery',
                items: [
                    {
                        xtype: 'combobox',
                        editable: false,
                        store: Store,
                        displayField: 'title',
                        valueField: 'id',
                        id: 'frog_gallery_id'
                    }
                ]
            }],
            buttons: [{
                text: 'Send',
                handler: function() {
                    var data = fp.getForm().getValues();
                    data.id = data['frog_gallery_id-inputEl'];
                    if (data.title !== "") {
                        var private = (data.private === 'on') ? true : false;
                        new Request.JSON({
                            url: '/frog/gallery',
                            async: false,
                            onSuccess: function(res) {
                                data.id = res.value.id;
                            }
                        }).POST({title: data.title, description: data.description, private: private});
                    }
                    var selected = $$('.thumbnail.selected');
                    guids = [];
                    selected.each(function(item) {
                        guids.push(item.dataset.frog_guid);
                    });
                    new Request.JSON({
                        url: '/frog/gallery/' + data.id,
                        emulation: false,
                        async: false,
                        onSuccess: function(res) {
                            Store.sync();
                            Ext.MessageBox.confirm('Confirm', 'Would you like to visit this gallery now?', function(res) {
                                if (res === 'yes') {
                                    window.location = '/frog/gallery/' + data.id;
                                }
                            });
                        }
                    }).PUT({guids: guids.join(',')});
                    win.close();
                }
            },{
                text: 'Cancel',
                handler: function() {
                    win.close();
                }
            }]
        });
        win.add(fp);
    }
    function downloadHandler() {
        var selected = $$('.thumbnail.selected');
        guids = [];
        selected.each(function(item) {
            guids.push(item.dataset.frog_guid);
        });
        location.href = '/frog/download?guids=' + guids.join(',');
    }
    function switchArtistHandler() {
        var win = Ext.create('widget.window', {
            title: 'Switch Artist',
            closable: true,
            closeAction: 'hide',
            resizable: false,
            modal: true,
            width: 400,
            height: 200,
            bodyStyle: 'padding: 5px;'
        });
        win.show();
        var input = new Element('input', {autofocus: 'autofocus', placeholder: "Search"});

        var fp = Ext.create('Ext.FormPanel', {
            items: [{
                xtype: 'label',
                text: "Start typing the name of an artist or if this is a new artist, type in the first and last name and click Send"
            }, {
                xtype: 'textfield',
                fieldLabel: 'Artist Name',
                id: 'frog_switch_artist'
            }],
            buttons: [{
                text: 'Send',
                handler: function() {
                    switchArtistCallback(input.value);
                    win.close();
                }
            },{
                text: 'Cancel',
                handler: function() {
                    win.close();
                }
            }]
        });
        win.add(fp);
        var input = $('frog_switch_artist-inputEl');
        new Meio.Autocomplete(input, '/frog/artistlookup', {
            requestOptions: {
                headers: {"X-CSRFToken": Cookie.read('csrftoken')},
            },
            filter: {
                path: 'name',
                formatItem: function(text, data) {
                    if (data.id === 0) {
                        return '<span class="search"></span>' + data.name
                    }
                    else {
                        return '<span></span>' + data.name
                    }
                }
            }
        });
        input.focus();
    }
    function rssHandler() {
        var win = Ext.create('widget.window', {
            title: 'RSS Feeds',
            icon: FrogStaticRoot + '/frog/i/feed.png',
            closable: true,
            closeAction: 'hide',
            resizable: false,
            modal: true,
            width: 400,
            height: 200,
            bodyStyle: 'padding: 5px;'
        });
        win.show();
        var fp = Ext.create('Ext.FormPanel', {
            defaultType: 'radio',
            items: [{
                xtype: 'label',
                text: "Select a feed frequency you'd like to subscribe to and the images will be available through Outlook",
                height: 100
            },
            {
                boxLabel: 'Daily',
                name: 'rss_int',
                inputValue: 'daily'
            }, {
                checked: true,
                boxLabel: 'Weekly',
                name: 'rss_int',
                inputValue: 'weekly'
            }],
            buttons: [{
                text: 'Save',
                handler: function() {
                    var r = fp.getForm().getValues(true).split('=')[1];
                    location.href = 'feed://' + location.host + '/frog/rss/' + ID + '/' + r;
                    win.close();
                }
            },{
                text: 'Cancel',
                handler: function() {
                    win.close();
                }
            }]
        });
        win.add(fp)
    }
    function helpHandler() {
        var win = Ext.create('widget.window', {
            title: 'Ask for Help',
            icon: FrogStaticRoot + '/frog/i/help.png',
            closable: true,
            closeAction: 'hide',
            resizable: false,
            modal: true,
            width: 600,
            height: 400,
            bodyPadding: 10,
            bodyStyle: 'padding: 5px; background: transparent;'
        });
        win.show();
        win.add({
            xtype: 'label',
            text: "Have a question, problem or suggestion?",
            style: {
                'font-size': '14px',
                'font-weight': 'bold'
            }
        })
        var fp = Ext.create('Ext.FormPanel', {
            items: [
            {
                xtype: 'textareafield',
                name: 'message',
                anchor: '100%',
                height: 300
            }],
            buttons: [{
                text: 'Send',
                handler: function() {
                    var data = fp.getForm().getValues();
                    new Request({
                        url: '/frog/help/',
                        headers: {"X-CSRFToken": Cookie.read('csrftoken')}
                    }).POST(data);
                    win.close();
                }
            },{
                text: 'Cancel',
                handler: function() {
                    win.close();
                }
            }]
        });
        win.add(fp)
    }
    function addPrivateMenu() {
        var id = this.id;
        this.menu.add({
            text: 'Make public',
            icon: FrogStaticRoot + '/frog/i/page_white_copy.png',
            handler: function() {
                Ext.MessageBox.confirm('Confirm', 'Are you sure you want to make this public?', function(res) {
                    if (res === 'yes') {
                        new Request.JSON({
                            url: '/frog/gallery/' + id,
                            emulation: false,
                            headers: {"X-CSRFToken": Cookie.read('csrftoken')}
                        }).PUT({private: false})
                    }
                });
            }
        });
    }
    function switchArtistCallback(name) {
        var selected = $$('.thumbnail.selected');
        guids = [];
        selected.each(function(item) {
            guids.push(item.dataset.frog_guid);
        });
        new Request.JSON({
            url: '/frog/switchartist',
            headers: {"X-CSRFToken": Cookie.read('csrftoken')},
            //async: false,
            onSuccess: function(res) {
                if (res.isSuccess) {
                    selected.each(function(el) {
                        var tag = el.getElement('.frog-tag');
                        tag.set('text', res.value.name.capitalize());
                        tag.dataset.frog_tag_id = res.value.tag;
                    });
                }
            }
        }).POST({'artist': name.toLowerCase(), guids: guids.join(',')});
        selected.each(function(el) {
            var tag = el.getElement('.frog-tag');
            tag.set('text', name.capitalize());
            tag.dataset.frog_tag_id = Frog.Tags.get(name.toLowerCase());
        });
    }

    

    // -- API
    var api = {
        render: render,
        setId: setId,
        toolbar: ToolBar,
        addEvent: addEvent,
        addTool: addTool
    };

    return api;

})(window.Frog);