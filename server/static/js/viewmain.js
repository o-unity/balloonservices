/**
 * Created by andi on 03.03.16.
 */


var viewmain_data = {
    type: "wide",
    id: "viewmain_sub",
    rows: [{
        type: "wide",
        height: "48%",
        id: "panels",
        cols: [{
            type:"clean",
            "css": "webix_view_box image_box",
            id: "imgwindow",
            rows:[
                {
                    "template": "<div class='click100'><span class='webix_icon fa-file-image-o' style='padding-right: 20px'></span>last image</div>",
                    "css": "sub_title",
                    "height": 40,
                    id: "imglistwindow",
                    onClick: {
                        "click100": function (e, id, trg) {
                            //webix.message("Delete row: " + id);
                            $$('viewimage').show();
                            //return false; //here it blocks default behavior
                        }
                    }
                },
                {
                    template: "<div class='imgnospace'><div class='imgtimestamp'>15:35:10</div></div>", css: "imgnospace",
                    id: "imgpopuplink"
                }
            ]

        }, {
            type:"clean",
            "css": "webix_view_box",
            rows:[
                {
                    "template": "<span class='webix_icon fa-map-marker' style='padding-right: 20px'></span>google map path",
                    "css": "sub_title",
                    "height": 40
                },
                {
                    template: "html->gmapcontainer",
                    id: "gmapview"
                }
            ]
        }]
    },{
        type: "wide",
        height: "52%",
        id: "panels",
        cols: [{
            type:"clean",
            "css": "webix_view_box",
            rows:[
                {
                    "template": "<span class='webix_icon fa-line-chart' style='padding-right: 20px'></span>altitude / speed",
                    "css": "sub_title",
                    "height": 40
                },
                {
                    template: "altitude / speed"
                }
            ]
        }, {
            type:"clean",
            "css": "webix_view_box",
            rows:[
                {
                    "template": "<span class='webix_icon fa-file-text-o' style='padding-right: 20px'></span>log",
                    "css": "sub_title",
                    "height": 40
                },
                {
                    template: "html->boxctlog",
                    id: "boxctlog",
                    scroll: true,
                }
            ]
        }]
    }]
};

$(document).ready(function(){
    $$('action_cleanup').attachEvent("onItemClick", function(id,value){
        webix.confirm({
            title:"cleanup database",
            ok:"Yes",
            cancel:"No",
            text:"are you sure to cleanup <br>the <b>database</b>?<br><br>You will lose all received data!",
            callback: function(result){
                if(result){
                    socket.emit('cleanup', {
                        'loggingtype':  'cleanup',
                        'uuid':         webix.storage.cookie.get('uuid')
                    });
                    webix.message("database is now empty");
                }
            }
        });
    });

    $$('action_login').attachEvent("onItemClick", function(id,value){
        $$('log_form_window').show();
    });
});

function addmsg2log(msg){
   logarr.push(msg);

    var htmltext = ""
    if(logarr.length > 100){
       logarr.splice(0, 1);
    }

    for (var i = logarr.length-1; i > -1; i--) {
        htmltext += logarr[i] + "<br>"
    }

    $('#boxctlogtext').html(htmltext)
    $$('boxctlog').define("template","html->boxctlog");
    $$('boxctlog').refresh();
}

function addimg2main(id){
    $('.image_box').css('backgroundImage','url(/getimage?id=' + id + ')');
    //console.log($('.image_box').css('background-image'))
}