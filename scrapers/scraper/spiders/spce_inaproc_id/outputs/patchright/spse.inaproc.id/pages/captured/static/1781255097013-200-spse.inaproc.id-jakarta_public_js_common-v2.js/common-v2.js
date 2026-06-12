$(function(){
  $(document).on('hidden.bs.modal', '.modal', function () {
    $(this).removeData('bs.modal');
  });
  $(document).on("click",".jpopup", function(){
    var height = $(this).attr('height');
    var width  = $(this).attr('width');
    if(typeof height == 'undefined')
      height = 400;
    if(typeof width=='undefined')
      width = 830;
    console.log(height);
    newwindow=window.open($(this).attr('href'),'','height='+height+',width='+width+'status=yes,toolbar=no,resizable=yes,location=no,scrollbars=yes');
    if (window.focus) {newwindow.focus()}
    return false;
  });

  $(".checkall").click(function(){
    $('input:checkbox').not(this).prop('checked', this.checked);
  });

  $(".checkall_auditor").click(function(){
    $('.check_auditor').not(this).prop('checked', this.checked);
  });

  $(".checkall_paket").click(function(){
    $('.check_paket').not(this).prop('checked', this.checked);
  });

  $(".checkall_peserta").click(function(){
    $('.check_peserta').not(this).prop('checked', this.checked);
  });

  $(".checkall_lelang").click(function(){
    $('.check_lelang').not(this).prop('checked', this.checked);
  });

  $('#npwp').on("click input", function () {
    // Strip non-digits and limit to 16
    var value = $(this).val().replace(/\D/g, '').substring(0, 16);

    // Set validity if less than 15 digits
    if (value.length < 15) {
        this.setCustomValidity("NPWP yang diisi harus terdiri dari 15 digit atau 16 digit. Silakan periksa kembali.");
    } else {
        this.setCustomValidity('');
    }

    // Format the value based on length
    var formattedValue = '';
    if (value.length <= 15) {
        // Format: 99.999.999.9-999.999
        formattedValue = value.replace(/(\d{2})(\d{3})(\d{3})(\d{1})(\d{3})(\d{3})/, '$1.$2.$3.$4-$5.$6');
    } else {
        // Format: 999.999.999.9-999.999
        // formattedValue = value.replace(/(\d{3})(\d{3})(\d{3})(\d{1})(\d{3})(\d{3})/, '$1.$2.$3.$4-$5.$6');
        formattedValue = value
    }

    // Update the input value
    $(this).val(formattedValue);
  });

  $('.carousel').carousel();
  //logout
  $("#logout").click(function(){
    $("#formLogout").submit();
  });
  $(document).on('click', '.remove', function(){
    $(this).parent().parent().remove()
  })
  $(document).on('click', '#tambahIjin', function(){
    var idx = $('#tblIjinUsaha').find(".ijin").length
    var addIjin = '<tr ><td><input type="text" name="ijin['+idx+'].chk_nama" id="ijin-nama-'+idx+'" class="form-control ijin"/></td>'+
      '<td><input type="text" name="ijin['+idx+'].chk_klasifikasi" class="form-control"></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td></tr>'
    $("#tblIjinUsaha").append(addIjin);
    $("#ijin-nama-" + idx).focus();
  })
  $(document).on('click', '#tambahSyarat', function(){
    var idx = $('#tblSyarat').find(".syarat").length
    var addIjin = '<tr class="syarat">'+
      '<td><input type="checkbox" name="checklist['+idx+'].ckm_id" value="28" /></td>'+
      '<td><textarea name="checklist['+idx+'].chk_nama" cols="80" rows="2" class="form-control"></textarea><span class="warning"><em>*Pastikan syarat tambahan sudah di ceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>'
    $('#tblSyarat').append(addIjin);
  });
  $(document).on('click', '#tambahSyaratAdmin', function(){
    var idx = $('#tblSyaratAdmin').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratAdmin['+idx+'].ckm_id" value="995" />'+
      '<input type="hidden" name="checklist_kualifikasi_administrasi_ckm_id['+idx+']" value="995"/></td>'+
      '<td><input type="text" class="form-control" name="syaratAdmin['+idx+'].chk_nama" />'+
      '<span class="warning"><em>*pastikan syarat tambahan sudah diceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblSyaratAdmin').append(add);
  });
  $(document).on('click', '#tambahSyaratAdminPerorangan', function(){
    var idx = $('#tblSyaratAdmin').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratAdmin['+idx+'].ckm_id" value="993" />'+
      '<input type="hidden" name="checklist_kualifikasi_administrasi_ckm_id['+idx+']" value="993"/></td>'+
      '<td><input type="text" class="form-control" name="syaratAdmin['+idx+'].chk_nama" />'+
      '<span class="warning"><em>*pastikan syarat tambahan sudah diceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblSyaratAdmin').append(add);
  });
  $(document).on('click', '#tambahPersyaratanKualifikasi', function(){
    var idx = $('#tblSyaratAdmin').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratAdmin['+idx+'].ckm_id" value="998" checked />'+
      '<input type="hidden" name="checklist_kualifikasi_administrasi_ckm_id['+idx+']" value="998"/></td>'+
      '<td><input type="text" class="form-control" id="syaratAdmin'+idx+'" name="syaratAdmin['+idx+'].chk_nama" />'+
      '<span class="warning d-none"><em>*pastikan syarat tambahan sudah diceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblSyaratAdmin').append(add);
    $("#syaratAdmin" + idx).focus();
  });
  $(document).on('click', '#tambahSyaratTeknis', function(){
    var idx = $('#tblSyaratTeknis').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratTeknis['+idx+'].ckm_id" value="996" checked />'+
      '<input type="hidden" name="checklist_kualifikasi_teknis_ckm_id['+idx+']" value="996"/></td>'+
      '<td><input type="text" class="form-control" id="syaratTeknis'+idx+'" name="syaratTeknis['+idx+'].chk_nama" />'+
      '<span class="warning d-none"><em>*pastikan syarat tambahan sudah diceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblSyaratTeknis').append(add);
    $("#syaratTeknis" + idx).focus();
  });
  $(document).on('click', '#tambahSyaratTeknisPerorangan', function(){
    var idx = $('#tblSyaratTeknis').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratTeknis['+idx+'].ckm_id" value="994" checked />'+
      '<input type="hidden" name="checklist_kualifikasi_teknis_ckm_id['+idx+']" value="994"/></td>'+
      '<td><input type="text" class="form-control" id="syaratTeknis'+idx+'" name="syaratTeknis['+idx+'].chk_nama" />'+
      '<span class="warning d-none"><em>*pastikan syarat tambahan sudah diceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblSyaratTeknis').append(add);
    $("#syaratTeknis" + idx).focus();
  });
  $(document).on('click', '#tambahSyaratKeuangan', function(){
    var idx = $('#tblSyaratKeuangan').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratKeuangan['+idx+'].ckm_id" value="997" />'+
      '<input type="hidden" name="checklist_kualifikasi_keuangan_ckm_id['+idx+']" value="997"/></td>'+
      '<td><input type="text" class="form-control" name="syaratKeuangan['+idx+'].chk_nama" />'+
      '<span class="warning"><em>*pastikan syarat tambahan sudah diceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblSyaratKeuangan').append(add)
  });
  $(document).on('click', '#tambahAdmin', function(){
    var idx = $('#tblAdmin').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratAdmin['+idx+'].ckm_id" value="30" /></td>'+
      '<td><input type="text" class="form-control" name="syaratAdmin['+idx+'].chk_nama" /></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblAdmin').append(add)
  });
  $(document).on('click', '#tambahTeknis', function(){
    var idx = $('#tblTeknis').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syarat['+idx+'].ckm_id" value="999" /></td>'+
      '<input type="hidden" name="checklist_teknis_ckm_id['+idx+']" value="999"/>'+
      '<td><input type="text" class="form-control" required name="syarat['+idx+'].chk_nama" maxlength="70"/><span class="warning"><em>*Pastikan syarat tambahan sudah di ceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblTeknis').append(add) ;
  });
  $(document).on('click', '#tambahTeknisPl', function(){
    var idx = $('#tblTeknis').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syarat['+idx+'].ckm_id" value="36" /></td>'+
      '<td><input type="text" class="form-control" required name="syarat['+idx+'].chk_nama" required/><span class="warning"><em>*Pastikan syarat tambahan sudah di ceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblTeknis').append(add) ;
  });
  $(document).on('click', '#tambahTeknisPlJKBU', function(){
    var idx = $('#tblTeknis').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syarat['+idx+'].ckm_id" value="510" /></td>'+
      '<td><input type="text" class="form-control" required name="syarat['+idx+'].chk_nama" required/><span class="warning"><em>*Pastikan syarat tambahan sudah di ceklist sebelum menyimpan</em></span></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblTeknis').append(add) ;
  });
  $(document).on('click', '#tambahHarga', function(){
    var idx = $('#tblHarga').find(".syarat").length;
    var add = '<tr class="syarat">'+
      '<td><input type="checkbox" name="syaratHarga['+idx+'].ckm_id" value="31" /></td>'+
      '<td><input type="text" class="form-control" name="syaratHarga['+idx+'].chk_nama" /></td>'+
      '<td><a href="javascript:void(0)" class="remove"><i class="fa fa-trash-o fa-lg"></i></a></td>'+
      '</tr>';
    $('#tblHarga').append(add);
  });

  $(document).on('click', '.dialog-input', function(){
    var _this = $(this);
    var refid = $(this).attr("refid");
    var data = $('#'+refid).val();
    var tipe = $(this).attr("tipe");
    var pesanval="";
    if(refid=="field1"){
      var pesanval = "(pastikan Nilai field divisi di input 2 digit)";
    }
    else if(refid=="field2"){
      var pesanval = "(pastikan Nilai field kelompok harus 3 digit)";
    }
    var keyp = (tipe=="form-text") ? '' : 'onkeypress="validate(event)"';
    var title = $(this).attr("title");
    BootstrapDialog.show({
      title: title,
      message: 'Data '+pesanval+': <input id="input-'+refid+'" class="form-control '+tipe+'" value="'+data+'" type="text" '+keyp+' >',
      data: {
        'close': false
      },
      closable : false,
      onshown : function(dialog) {
        if (tipe == "form-number" && ($('#'+refid).val()=="" || $('#'+refid).val()==0))
          $('#input-'+refid).val('1');
        else if (tipe == "form-number-tahun" && ($('#'+refid).val()=="" || $('#'+refid).val()==0))
          $('#input-'+refid).val('4');
        $('#input-'+refid).focus();
      },
      onhide: function(dialog){
        if (dialog.getData('close'))
          return true;
        var input = dialog.getModalBody().find('input').val();
        $('#'+refid).val(input);
        if(input != '') {
          _this.html("<b> "+input+" </b>");
        } else {
          alert('Data wajib diisi!');
          $('#input-'+refid).focus();
          return false;
        }
      },
      buttons: [{
        label: '✓',
        cssClass: 'btn-primary',
        action: function(dialog) {
          dialog.close();
        }
      }, {
        label: '✘',
        action: function(dialog) {
          dialog.setData('close', true);
          dialog.close();
        }
      }]
    });
    return false;
  });

  // dialog message. usage <a href=".." class="dialog">nama link</a>
  $(document).on('click', '.dialog', function(){
    var href = $(this).attr("href");
    var title = $(this).attr("title");
    var onhide = $(this).attr("onhide-refresh");
//        console.log('before : ' +onhide)
    BootstrapDialog.show({
      size: BootstrapDialog.SIZE_WIDE,
      title:title,
      message:$('<div id="popupContent"></div>'),
      draggable : true,
      closable : false,
      onshown: function () {
        $("#popupContent").load(href)
      },
      onhide : function(dialog) {
        // console.log(onhide)
        if(onhide) {
          //console.log('reload page...')
          location.reload();
        }
      },
      buttons: [{
        label: 'Close',
        cssClass: 'btn btn-secondary bootstrap4-dialog-button',
        action: function(dialogItself){
          dialogItself.close();
        }
      }]
    });
    return false;
  });

  $(document).on('click', '.dialogCR', function(){
    var href = $(this).attr("href");
    var title = $(this).attr("title");
    var onhide = $(this).attr("onhide-refresh");
//        console.log('before : ' +onhide)
    BootstrapDialog.show({
      size: BootstrapDialog.SIZE_WIDE,
      title:title,
      message:$('<div id="popupContent"></div>'),
      draggable : true,
      closable : false,
      onshown: function () {
        $("#popupContent").load(href)
      },
      onhide : function(dialog) {
        // console.log(onhide)
        if(onhide) {
          //console.log('reload page...')
          location.reload();
        }
      },
      buttons: [{
        label: 'Close',
        cssClass: 'btn btn-secondary bootstrap4-dialog-button',
        action: function(dialogItself){
          dialogItself.close();
          location.reload();
        }
      }]
    });
    return false;
  });
  $(document).on('click', '.confirm', function(){
    var obj = $(this)
    var title = obj.attr("title");
    var href = obj.attr("href");
    var type = obj.attr("typeW");
    if (typeof type == typeof undefined && type == false) {
      type = "type-primary";
    }
    BootstrapDialog.confirm({
      type : type,
      title: 'Konfirmasi',
      message: title,
      draggable: true,
      closable: true,
      closeByBackdrop: false,
      closeByKeyboard: false,
      btnOKLabel: 'Ya',
      btnCancelLabel: 'Tidak',
      callback : function(result){
        if(result) {
          if (typeof href !== typeof undefined && href !== false) {
            window.location.href=href
          } else {
            obj.parents('form').submit()
          }
        }
      }
    });
    return false;
  });
  if(!!$("#showHideHeader").length)
    setHeaderVisibility();
  $("#showHideHeader").click(function(){
    var headerVisible=$.cookie("headerVisible");
    if(headerVisible === null)
      headerVisible = 'true';
    else
      headerVisible = headerVisible=='true' ? 'false':'true';
    $.cookie('headerVisible', headerVisible);
    setHeaderVisibility();
    return false;
  });

  function setHeaderVisibility()
  {
    var headerVisible=$.cookie("headerVisible");
    var imgSrc=$("#showHideHeader i").attr("class");
    if(headerVisible == 'true' || headerVisible == null)
    {
      $("#headerContent").show();
      imgSrc=imgSrc.replace("fa fa-angle-double-down","fa fa-angle-double-up");
      $("#showHideHeader i").attr("class",imgSrc);
    }
    else
    {
      $("#headerContent").hide();
      imgSrc=imgSrc.replace("fa fa-angle-double-up","fa fa-angle-double-down")	;
      $("#showHideHeader i").attr("class",imgSrc);
    }
  }
  $(document).on('mousedown', '.glyphicon-eye-open', function(){
    $(".passwordfield").attr('type','text');
  }).mouseup(function(){$(".passwordfield").attr('type','password');}).mouseout(function(){$(".passwordfield").attr('type','password');});
});
function toRupiah(jumlah)
{
  return "Rp. "+toRupiah2(jumlah);
}

function toRupiahUSA(jumlah)
{
  return "Rp. "+toRupiah3(jumlah);
}

function toRupiah2(jumlah)
{
  var split = jumlah.toString().replace('.',',').split(',');
  var rev = split[0].split("").reverse().join("");
  var rev2  = "";
  for(var i = 0; i < rev.length; i++){
    rev2  += rev[i];
    if((i + 1) % 3 === 0 && i !== (rev.length - 1)){
      rev2 += ".";
    }
  }
  if(split[1] === undefined)
    split[1] = '00';
  return rev2.split("").reverse().join("")+","+split[1];
}

function toRupiah3(jumlah)
{
  var split = jumlah.toString().replace('.',',').split(',');
  var rev = split[0].split("").reverse().join("");
  var rev2  = "";
  for(var i = 0; i < rev.length; i++){
    rev2  += rev[i];
    if((i + 1) % 3 === 0 && i !== (rev.length - 1)){
      rev2 += ",";
    }
  }
  return rev2.split("").reverse().join("")+"."+split[1];
}

function replaceAll(string, token, newtoken) {
  if(token!=newtoken)
    while(string.indexOf(token) > -1) {
      string = string.replace(token, newtoken);
    }
  return string;
}

function toNumber(string) {
  if(string && (string.length > 0)) {
    string = replaceAll(string,'Rp ','');
    string = replaceAll(string,'Rp. ','');
    string = replaceAll(string,'.','');
    string = replaceAll(string,',','.');
    return parseFloat(string);
  }
  return 0;
}

function autoCloseAlert() {
  $('.alert[data-auto-dismiss]').each(function (index, element) {
    var $element = $(element),
      timeout  = $element.data('auto-dismiss') || 5000;

    setTimeout(function () {
      $element.alert('close');
    }, timeout);
  });
}

function getLabelSpseVersion(flag){
  var data = {flag:'',highlight:''};

  if(flag =='5') {
      data.flag = 'spse 4.5';
      data.highlight = 'badge badge-info';
  }
  else if(flag =='4') {
    data.flag = 'spse 4.4';
    data.highlight = 'badge badge-warning';
  }
  else if(flag =='3') {
    data.flag = 'spse 4.3';
    data.highlight = 'badge badge-danger';
  }
  else if(flag == '2'){
    data.flag = 'spse 4';
    data.highlight = 'badge badge-success';
  }
  else{
    data.flag = 'spse 3';
    data.highlight = 'badge badge-success';
  }

  return data;
}

function getKonsolidasiLabel() {
  var data = {
    flag:'Konsolidasi',
    highlight:'badge badge-primary'
  };
  return data
}

function rounded2Decimal(value) {
  if(isNaN(value)){
    return 0;
  }
  return Math.round(value * 100) / 100;
}

function isNumberKey(evt){
  var charCode = (evt.which) ? evt.which : evt.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57))
    return false;
  return true;
}

function readOnlyCheckBox() {
   return false;
}

function leftPad(number, targetLength) {
  var output = number + '';
  while (output.length < targetLength) {
    output = '0' + output;
  }
  return output;
}
