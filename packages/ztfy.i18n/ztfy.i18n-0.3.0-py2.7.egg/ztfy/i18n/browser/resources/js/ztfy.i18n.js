/**
 * I18n tabs management
 * Mainly based on MCTabs from TinyMCE HTML editor project
 */
function I18nTabs() {
	this.settings = new Array();
	this.tabs = new Array();
};

I18nTabs.prototype.init = function(settings) {
	this.settings = settings;
};

I18nTabs.prototype.getParam = function(name, default_value) {
	var value = null;

	value = (typeof(this.settings[name]) == "undefined") ? default_value : this.settings[name];

	// Fix bool values
	if (value == "true" || value == "false")
		return (value == "true");

	return value;
};

I18nTabs.prototype.displayTab = function(tab_id) {
	var panelElm = document.getElementById('I18nTab_' + tab_id);
	var panelContainerElm = panelElm ? panelElm.parentNode : null;
	var tabElm = document.getElementById('I18nHeader_' + tab_id);
	var tabContainerElm = tabElm ? tabElm.parentNode : null;
	var selectionClass = this.getParam('selection_class', 'current');

	if (tabElm && tabContainerElm) {
		var nodes = tabContainerElm.childNodes;

		// Hide all other tabs
		for (var i=0; i<nodes.length; i++) {
			if (nodes[i].nodeName == "LI")
				$(nodes[i]).removeClass(selectionClass);
		}

		// Show selected tab
		$(tabElm).addClass(selectionClass);
	}

	if (panelElm && panelContainerElm) {
		var nodes = panelContainerElm.childNodes;

		// Hide all other panels
		for (var i=0; i<nodes.length; i++) {
			if (nodes[i].nodeName == "DIV")
				$(nodes[i]).removeClass(selectionClass);
		}

		// Show selected panel
		$(panelElm).addClass(selectionClass);
	}
};

I18nTabs.prototype.getAnchor = function() {
	var pos, url = document.location.href;

	if ((pos = url.lastIndexOf('#')) != -1)
		return url.substring(pos + 1);

	return "";
};

I18nTabs.prototype.switchTabs = function(name) {
	var control = document.getElementById('I18nControl_' + name);
	var ul = control.getElementsByTagName('UL')[0];
	var childs = ul.getElementsByTagName('LI');
	var mode;
	var selectionClass = this.getParam('selection_class', 'current');
	for (var i=1; i<childs.length; i++) {
		if ($(childs[i]).hasClass(selectionClass)) {
			var id = childs[i].id;
			var pos = id.indexOf('_');
			this.tabs[name] = id.substr(pos+1);
		}
		if (childs[i].style.display == '') {
			childs[i].style.display = 'none';
			mode = 'all';
		}
		else {
			childs[i].style.display = '';
			mode = 'single';
		}
	}
	var panel = document.getElementById('I18nPanel_' + name);
	var lang_tabs = panel.getElementsByTagName('DIV');
	for (var it=0; it<lang_tabs.length; it++) {
		if ($(lang_tabs[it]).hasClass('panel_flag')) {
			if (mode == 'all')
				lang_tabs[it].style.display = 'block';
			else
				lang_tabs[it].style.display = '';
		}
		if (lang_tabs[it].parentNode == panel) {
			if (mode == 'all')
				$(lang_tabs[it]).addClass(selectionClass);
			else
				$(lang_tabs[it]).removeClass(selectionClass);
		}
	}
	$(lang_tabs['I18nTab_' + this.tabs[name]]).addClass(selectionClass);
};

// Global instance
var i18nTabs = new I18nTabs();
