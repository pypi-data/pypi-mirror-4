﻿/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.dialog.add('select',function(a){function b(k,l,m,n,o){k=j(k);var p;if(n)p=n.createElement('OPTION');else p=document.createElement('OPTION');if(k&&p&&p.getName()=='option'){if(CKEDITOR.env.ie){if(!isNaN(parseInt(o,10)))k.$.options.add(p.$,o);else k.$.options.add(p.$);p.$.innerHTML=l.length>0?l:'';p.$.value=m;}else{if(o!==null&&o<k.getChildCount())k.getChild(o<0?0:o).insertBeforeMe(p);else k.append(p);p.setText(l.length>0?l:'');p.setValue(m);}}else return false;return p;};function c(k){k=j(k);var l=g(k);for(var m=k.getChildren().count()-1;m>=0;m--){if(k.getChild(m).$.selected)k.getChild(m).remove();}h(k,l);};function d(k,l,m,n){k=j(k);if(l<0)return false;var o=k.getChild(l);o.setText(m);o.setValue(n);return o;};function e(k){k=j(k);while(k.getChild(0)&&k.getChild(0).remove()){}};function f(k,l,m){k=j(k);var n=g(k);if(n<0)return false;var o=n+l;o=o<0?0:o;o=o>=k.getChildCount()?k.getChildCount()-1:o;if(n==o)return false;var p=k.getChild(n),q=p.getText(),r=p.getValue();p.remove();p=b(k,q,r,!m?null:m,o);h(k,o);return p;};function g(k){k=j(k);return k?k.$.selectedIndex:-1;};function h(k,l){k=j(k);if(l<0)return null;var m=k.getChildren().count();k.$.selectedIndex=l>=m?m-1:l;return k;};function i(k){k=j(k);return k?k.getChildren():false;};function j(k){if(k&&k.domId&&k.getInputElement().$)return k.getInputElement();else if(k&&k.$)return k;return false;};return{title:a.lang.select.title,minWidth:CKEDITOR.env.ie?460:395,minHeight:CKEDITOR.env.ie?320:300,onShow:function(){var n=this;delete n.selectBox;n.setupContent('clear');var k=n.getParentEditor().getSelection().getSelectedElement();if(k&&k.getName()=='select'){n.selectBox=k;n.setupContent(k.getName(),k);var l=i(k);for(var m=0;m<l.count();m++)n.setupContent('option',l.getItem(m));}},onOk:function(){var k=this.getParentEditor(),l=this.selectBox,m=!l;if(m)l=k.document.createElement('select');this.commitContent(l);if(m){k.insertElement(l);if(CKEDITOR.env.ie){var n=k.getSelection(),o=n.createBookmarks();setTimeout(function(){n.selectBookmarks(o);},0);}}},contents:[{id:'info',label:a.lang.select.selectInfo,title:a.lang.select.selectInfo,accessKey:'',elements:[{id:'txtName',type:'text',widths:['25%','75%'],labelLayout:'horizontal',label:a.lang.common.name,'default':'',accessKey:'N',style:'width:350px',setup:function(k,l){if(k=='clear')this.setValue(this['default']||'');else if(k=='select')this.setValue(l.data('cke-saved-name')||l.getAttribute('name')||'');},commit:function(k){if(this.getValue())k.data('cke-saved-name',this.getValue());
else{k.data('cke-saved-name',false);k.removeAttribute('name');}}},{id:'txtValue',type:'text',widths:['25%','75%'],labelLayout:'horizontal',label:a.lang.select.value,style:'width:350px','default':'',className:'cke_disabled',onLoad:function(){this.getInputElement().setAttribute('readOnly',true);},setup:function(k,l){if(k=='clear')this.setValue('');else if(k=='option'&&l.getAttribute('selected'))this.setValue(l.$.value);}},{type:'hbox',widths:['175px','170px'],children:[{id:'txtSize',type:'text',labelLayout:'horizontal',label:a.lang.select.size,'default':'',accessKey:'S',style:'width:175px',validate:function(){var k=CKEDITOR.dialog.validate.integer(a.lang.common.validateNumberFailed);return this.getValue()===''||k.apply(this);},setup:function(k,l){if(k=='select')this.setValue(l.getAttribute('size')||'');if(CKEDITOR.env.webkit)this.getInputElement().setStyle('width','86px');},commit:function(k){if(this.getValue())k.setAttribute('size',this.getValue());else k.removeAttribute('size');}},{type:'html',html:'<span>'+CKEDITOR.tools.htmlEncode(a.lang.select.lines)+'</span>'}]},{type:'html',html:'<span>'+CKEDITOR.tools.htmlEncode(a.lang.select.opAvail)+'</span>'},{type:'hbox',widths:['115px','115px','100px'],children:[{type:'vbox',children:[{id:'txtOptName',type:'text',label:a.lang.select.opText,style:'width:115px',setup:function(k,l){if(k=='clear')this.setValue('');}},{type:'select',id:'cmbName',label:'',title:'',size:5,style:'width:115px;height:75px',items:[],onChange:function(){var k=this.getDialog(),l=k.getContentElement('info','cmbValue'),m=k.getContentElement('info','txtOptName'),n=k.getContentElement('info','txtOptValue'),o=g(this);h(l,o);m.setValue(this.getValue());n.setValue(l.getValue());},setup:function(k,l){if(k=='clear')e(this);else if(k=='option')b(this,l.getText(),l.getText(),this.getDialog().getParentEditor().document);},commit:function(k){var l=this.getDialog(),m=i(this),n=i(l.getContentElement('info','cmbValue')),o=l.getContentElement('info','txtValue').getValue();e(k);for(var p=0;p<m.count();p++){var q=b(k,m.getItem(p).getValue(),n.getItem(p).getValue(),l.getParentEditor().document);if(n.getItem(p).getValue()==o){q.setAttribute('selected','selected');q.selected=true;}}}}]},{type:'vbox',children:[{id:'txtOptValue',type:'text',label:a.lang.select.opValue,style:'width:115px',setup:function(k,l){if(k=='clear')this.setValue('');}},{type:'select',id:'cmbValue',label:'',size:5,style:'width:115px;height:75px',items:[],onChange:function(){var k=this.getDialog(),l=k.getContentElement('info','cmbName'),m=k.getContentElement('info','txtOptName'),n=k.getContentElement('info','txtOptValue'),o=g(this);
h(l,o);m.setValue(l.getValue());n.setValue(this.getValue());},setup:function(k,l){var n=this;if(k=='clear')e(n);else if(k=='option'){var m=l.getValue();b(n,m,m,n.getDialog().getParentEditor().document);if(l.getAttribute('selected')=='selected')n.getDialog().getContentElement('info','txtValue').setValue(m);}}}]},{type:'vbox',padding:5,children:[{type:'button',id:'btnAdd',style:'',label:a.lang.select.btnAdd,title:a.lang.select.btnAdd,style:'width:100%;',onClick:function(){var k=this.getDialog(),l=k.getParentEditor(),m=k.getContentElement('info','txtOptName'),n=k.getContentElement('info','txtOptValue'),o=k.getContentElement('info','cmbName'),p=k.getContentElement('info','cmbValue');b(o,m.getValue(),m.getValue(),k.getParentEditor().document);b(p,n.getValue(),n.getValue(),k.getParentEditor().document);m.setValue('');n.setValue('');}},{type:'button',id:'btnModify',label:a.lang.select.btnModify,title:a.lang.select.btnModify,style:'width:100%;',onClick:function(){var k=this.getDialog(),l=k.getContentElement('info','txtOptName'),m=k.getContentElement('info','txtOptValue'),n=k.getContentElement('info','cmbName'),o=k.getContentElement('info','cmbValue'),p=g(n);if(p>=0){d(n,p,l.getValue(),l.getValue());d(o,p,m.getValue(),m.getValue());}}},{type:'button',id:'btnUp',style:'width:100%;',label:a.lang.select.btnUp,title:a.lang.select.btnUp,onClick:function(){var k=this.getDialog(),l=k.getContentElement('info','cmbName'),m=k.getContentElement('info','cmbValue');f(l,-1,k.getParentEditor().document);f(m,-1,k.getParentEditor().document);}},{type:'button',id:'btnDown',style:'width:100%;',label:a.lang.select.btnDown,title:a.lang.select.btnDown,onClick:function(){var k=this.getDialog(),l=k.getContentElement('info','cmbName'),m=k.getContentElement('info','cmbValue');f(l,1,k.getParentEditor().document);f(m,1,k.getParentEditor().document);}}]}]},{type:'hbox',widths:['40%','20%','40%'],children:[{type:'button',id:'btnSetValue',label:a.lang.select.btnSetValue,title:a.lang.select.btnSetValue,onClick:function(){var k=this.getDialog(),l=k.getContentElement('info','cmbValue'),m=k.getContentElement('info','txtValue');m.setValue(l.getValue());}},{type:'button',id:'btnDelete',label:a.lang.select.btnDelete,title:a.lang.select.btnDelete,onClick:function(){var k=this.getDialog(),l=k.getContentElement('info','cmbName'),m=k.getContentElement('info','cmbValue'),n=k.getContentElement('info','txtOptName'),o=k.getContentElement('info','txtOptValue');c(l);c(m);n.setValue('');o.setValue('');}},{id:'chkMulti',type:'checkbox',label:a.lang.select.chkMulti,'default':'',accessKey:'M',value:'checked',setup:function(k,l){if(k=='select')this.setValue(l.getAttribute('multiple'));
if(CKEDITOR.env.webkit)this.getElement().getParent().setStyle('vertical-align','middle');},commit:function(k){if(this.getValue())k.setAttribute('multiple',this.getValue());else k.removeAttribute('multiple');}}]}]}]};});
