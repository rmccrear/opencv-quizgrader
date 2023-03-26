//var image = $('#header-img').get(0);
/*
$image.cropper({
  aspectRatio: 16 / 9,
  crop: function(event) {
    console.log(event.detail.x);
    console.log(event.detail.y);
    console.log(event.detail.width);
    console.log(event.detail.height);
    console.log(event.detail.rotate);
    console.log(event.detail.scaleX);
    console.log(event.detail.scaleY);
  }
});
*/
// Get the Cropper.js instance after initialized
//var cropper = $image.data('cropper');


window.addEventListener('DOMContentLoaded', function () {
  var headerImage = document.querySelector('#header-img');
  var itemsImage =  document.querySelector('#items-img');
  const doneButton = document.querySelector('#done-btn');
  const cropperHeaders = new Cropper(headerImage, {
    //aspectRatio: 16 / 9,
    viewMode: 3,
    dragMode: 'move',
    autoCropArea: 1,
    restore: true,
    modal: true,
    guides: true,
    highlight: true,
    cropBoxMovable: true,
    cropBoxResizable: true,
    toggleDragModeOnDblclick: true,
    crop(event) {
      console.log(event.detail.x);
      console.log(event.detail.y);
      console.log(event.detail.width);
      console.log(event.detail.height);
      console.log(event.detail.rotate);
      console.log(event.detail.scaleX);
      console.log(event.detail.scaleY);
    },
  });
  const cropperItems = new Cropper(itemsImage, {
    //aspectRatio: 16 / 9,
    viewMode: 3,
    dragMode: 'move',
    autoCropArea: 1,
    restore: true,
    modal: true,
    guides: true,
    highlight: true,
    cropBoxMovable: true,
    cropBoxResizable: true,
    toggleDragModeOnDblclick: true,
    crop(event) {
      console.log(event.detail.x);
      console.log(event.detail.y);
      console.log(event.detail.width);
      console.log(event.detail.height);
      console.log(event.detail.rotate);
      console.log(event.detail.scaleX);
      console.log(event.detail.scaleY);
    },
  });
  doneButton.onclick = function(evt){
      const d = cropperItems.getData(true)
      console.log(d)
      const h = cropperHeaders.getData(true)
      const itemsRect   = [d.x, d.y, d.x+d.width, d.y+d.height]
      const headersRect = [h.x, h.y, h.x+h.width, h.y+h.height]
      console.log(itemsRect.join(','))
      console.log(headersRect.join(','))
      var headersInput = document.querySelector('input#headers-rect');
      var itemsInput = document.querySelector('input#items-rect');
      headersInput.value = headersRect.join(',')
      itemsInput.value = itemsRect.join(',')
      var rectForm = document.querySelector('form#rect-form');
      rectForm.submit();
  }
});