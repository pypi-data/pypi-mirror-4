/*
* Custom JavaScript Implementation.
*
* */


$(document).ready(function() {

    var add_user_options = {
        target:        '#add_user_output',   // target element(s) to be updated with server response
//        beforeSubmit:  showRequest,  // pre-submit callback
        success:       showResponse,  // post-submit callback
        clearForm: true,

        // other available options:
        //url:       url         // override for form's 'action' attribute
        //type:      type        // 'get' or 'post', override for form's 'method' attribute
        //dataType:  null        // 'xml', 'script', or 'json' (expected server response type)
        //clearForm: true        // clear all form fields after successful submit
        //resetForm: true        // reset the form after successful submit

        // $.ajax options can be used here too, for example:
        timeout:   3000
    };

    function showResponse() {
        $("#user_grid").setGridParam({page:1}).trigger("reloadGrid")
        alert("Successfully added user!");
        return;
    }
    function showRequest(formData, jqForm, add_user_options) {
        var queryString = $.param(formData);
        alert('Submitting: \n\n' + queryString);

        return true;
    }


    $("#user_grid").jqGrid({
        url:"/json/users.json",
        datatype: "json",
        mtype: 'GET',
        jsonReader: {
            root: "rows",
            page: "page",
            total: "total",
            records: "records",
            repeatitems: false,
            id: "5"  ,
            cell: ""  ,
            userdata: "userdata"
        },
        colNames:['ID', 'First Name','Last Name', 'Email', 'Permissions'],
        colModel:[{name:'id', index:'id', align:'center', width:55},
            {name:'first_name', index:'first_name', width:100},
            {name:'last_name', index:'last_name', width:100},
            {name:'email', index:'email', width:300},
            {name:'permissions', index:'permissions', width:100}
        ],
        rowNum:15,
        rowList:[10],
        pager: "#user_grid_pager",
        sortname: 'id',
        viewrecords: true,
        sortorder: "desc",
        gridview: true,
        width: '700',
        height: 'auto',
        caption: "System Users"
    });

    $("#user_grid").jqGrid('navGrid','#user_grid_pager',{edit:true,add:false,del:false});
    $('#add_user_form').ajaxForm(add_user_options);

});


