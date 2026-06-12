/**
 * reload source ajax
 * fnReloadAjax
 */
$.fn.dataTableExt.oApi.fnReloadAjax=function(g,d,h,c){if($.fn.dataTable.versionCheck){var e=new $.fn.dataTable.Api(g);if(d){e.ajax.url(d).load(h,!c)}else{e.ajax.reload(h,!c)}return}if(d!==undefined&&d!==null){g.sAjaxSource=d}if(g.oFeatures.bServerSide){this.fnDraw();return}this.oApi._fnProcessingDisplay(g,true);var f=this;var a=g._iDisplayStart;var b=[];this.oApi._fnServerParams(g,b);g.fnServerData.call(g.oInstance,g.sAjaxSource,b,function(l){f.oApi._fnClearTable(g);var j=(g.sAjaxDataProp!=="")?f.oApi._fnGetObjectDataFn(g.sAjaxDataProp)(l):l;for(var k=0;k<j.length;k++){f.oApi._fnAddData(g,j[k])}g.aiDisplay=g.aiDisplayMaster.slice();f.fnDraw();if(c===true){g._iDisplayStart=a;f.oApi._fnCalculateEnd(g);f.fnDraw(false)}f.oApi._fnProcessingDisplay(g,false);if(typeof h=="function"&&h!==null){h(g)}},g)};
/**
 * filter saat tekan enter
 * fnFilterOnReturn
 */
//$.fn.dataTableExt.oApi.fnFilterOnReturn=function(){var n=this;return this.each(function(t){$.fn.dataTableExt.iApiIndex=t;var i=$("input",n.fnSettings().aanFeatures.f);return i.unbind("keyup search input").bind("keypress",function(e){13==e.which&&($.fn.dataTableExt.iApiIndex=t,n.fnFilter(i.val()))}),this}),this};
jQuery.fn.dataTableExt.oApi.fnFilterOnReturn=function(n){var t=this;return this.each(function(n){$.fn.dataTableExt.iApiIndex=n;var i=$("input",t.fnSettings().aanFeatures.f);return i.unbind("keyup search input").bind("keypress",function(e){13==e.which&&($.fn.dataTableExt.iApiIndex=n,t.fnFilter(i.val()))}),this}),this};

$.extend( true, $.fn.dataTable.defaults, {
    order: [[ 0, "desc"]],
    processing: true,
    serverSide: true,
    pagingType: 'simple',
    pageLength : 25,
    lengthMenu: [[25, 50, 100], [25, 50, 100]],
    language : {
        paginate: {
            first:    '«',
            previous: '‹',
            next:     '›',
            last:     '»'
        },
        aria: {
            paginate: {
                first:    'First',
                previous: 'Previous',
                next:     'Next',
                last:     'Last'
            }
        },
        processing:   "Sedang proses...",
        sLengthMenu:   "Tampilan _MENU_ data",
        sZeroRecords:  "Tidak ditemukan data yang sesuai",
        sInfo:         "Tampilan _START_ sampai _END_",
        sInfoEmpty:    "Tampilan 0 hingga 0 dari 0 data",
        sInfoFiltered: "(disaring dari _MAX_ entri keseluruhan)",
        sInfoPostFix:  "",
        sSearch:       "Cari:",
    }
});
