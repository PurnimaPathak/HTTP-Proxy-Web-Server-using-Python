HTTP/1.1 200 OK
Date: Fri, 17 Nov 2017 17:44:27 GMT
Server: Apache
Last-Modified: Sun, 18 Aug 2002 03:26:26 GMT
ETag: "540b6f-c43-3a87405233c80"
Accept-Ranges: bytes
Content-Length: 3139
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: application/javascript



if (document.images) {            // Active Images

//On buttons

img1_on = new Image();
       img1_on.src = "buttons/about_on.jpg";                
img2_on = new Image();
       img2_on.src = "buttons/sponsors_on.gif";                        
img3_on = new Image();
       img3_on.src = "buttons/equip_on.gif";   
img4_on = new Image();
       img4_on.src = "buttons/media_on.gif";   
img5_on = new Image();
       img5_on.src = "buttons/sched_on.gif";                         
img6_on = new Image();
       img6_on.src = "buttons/distance_on.gif";      
img7_on = new Image();
       img7_on.src = "buttons/trg_on.gif";
img8_on = new Image();
       img8_on.src = "buttons/contactus_on.gif";

// Inside page on buttons
              
img9_on = new Image();
       img9_on.src = "inside/buttons/inside_on.jpg";     
img10_on = new Image();
       img10_on.src = "inside/buttons/equipment_on.jpg";     
img11_on = new Image();
       img11_on.src = "inside/buttons/sponsors_on.jpg";     
img12_on = new Image();
       img12_on.src = "inside/buttons/media_on.jpg";          
img13_on = new Image();
       img13_on.src = "inside/buttons/schedule_on.jpg";     
img14_on = new Image();
       img14_on.src = "inside/buttons/distance_on.jpg"; 
img15_on = new Image();
       img15_on.src = "inside/buttons/researchgroup_on.jpg"; 
img16_on = new Image();
       img16_on.src = "inside/buttons/contact_on.jpg";


// Off buttons
   
img1_off = new Image();
       img1_off.src = "buttons/about_off.jpg";   
img2_off = new Image();
       img2_off.src = "buttons/sponsors_off.gif";                
img3_off = new Image();
       img3_off.src = "buttons/equip_off.gif"; 
img4_off = new Image();
       img4_off.src = "buttons/media_off.gif"; 
img5_off = new Image();
       img5_off.src = "buttons/sched_off.gif";
img6_off = new Image();
       img6_off.src = "buttons/distance_off.gif"; 
img7_off = new Image();
       img7_off.src = "buttons/trg_off.gif";                          
img8_off = new Image();
       img8_off.src = "buttons/contactus_off.gif";

// Inside page off buttons
img9_off = new Image();
       img9_off.src = "inside/buttons/inside_off.jpg";
img10_off = new Image();
       img10_off.src = "inside/buttons/equipment_off.jpg";
img11_off = new Image();
       img11_off.src = "inside/buttons/sponsors_off.jpg";
img12_off = new Image();
       img12_off.src = "inside/buttons/media_off.jpg";
img13_off = new Image();
       img13_off.src = "inside/buttons/schedule_off.jpg";
img14_off = new Image();
       img14_off.src = "inside/buttons/distance_off.jpg";                
img15_off = new Image();
       img15_off.src = "inside/buttons/researchgroup_off.jpg";
img16_off = new Image();
       img16_off.src = "inside/buttons/contact_off.jpg";

}
//on.
function onImgs(imgName) {
        if (document.images) {
            document[imgName].src = eval(imgName + "_on.src");
        }
}
//off.
function offImgs(imgName) {
        if (document.images) {
            document[imgName].src = eval(imgName + "_off.src");
        }
}

