MathJax.Hub.Config({
  showProcessingMessages: false,
  tex2jax: { inlineMath: [['$','$'],['\\(','\\)']] }
});

var Preview = {
  delay: 150,        // delay after keystroke before updating

  preview: null,     // filled in by Init below
  buffer: null,      // filled in by Init below

  timeout: null,     // store setTimout id
  mjRunning: false,  // true when MathJax is processing
  oldText: null,     // used to check if an update is needed

  //
  //  Switch the buffer and preview, and display the right one.
  //  (We use visibility:hidden rather than display:none since
  //  the results of running MathJax are more accurate that way.)
  //
  SwapBuffers: function () {
    var buffer = this.preview, preview = this.buffer;
    this.buffer = buffer; this.preview = preview;
    $(this.buffer).hide();
    $(this.preview).show();
  },



  //
  //  Creates the preview and runs MathJax on it.
  //  If MathJax is already trying to render the code, return
  //  If the text hasn't changed, return
  //  Otherwise, indicate that MathJax is running, and start the
  //    typesetting.  After it is done, call PreviewDone.
  //  
  CreatePreview: function (textarea) {
    Preview.timeout = null;
    if (this.mjRunning) return;
    var text = $(textarea).value;
    this.preview = $(textarea).parent().find('.MathPreview');
    this.buffer = $(textarea).parent().find('.MathBuffer');
    if (text === this.oldtext) return;
    this.oldtext = text;
    $(this.buffer).html(text);
    this.mjRunning = true;
    MathJax.Hub.Queue(
      ["Typeset",MathJax.Hub,this.buffer],
      ["PreviewDone",this]
    );
  },

  //
  //  Indicate that MathJax is no longer running,
  //  and swap the buffers to show the results.
  //
  PreviewDone: function () {
    this.mjRunning = false;
    this.SwapBuffers();
  }

};

var CreatePreviewBo = function(textarea) {
    Preview.timeout = null;
    if (Preview.mjRunning) return;
    var text = textarea;
    if (text === Preview.oldtext) return;
    Preview.oldtext = text;
    $(Preview.buffer).html(text);
    Preview.mjRunning = true;
    MathJax.Hub.Queue(
      ["Typeset",MathJax.Hub,Preview.buffer],
      ["PreviewDone",Preview]
    );
}

//
//  Cache a callback to the CreatePreview action
//
Preview.callback = MathJax.Callback([CreatePreviewBo]);
Preview.callback.autoReset = true;  // make sure it can run more than once

$(document).ready(function(){
$('.MathBuffer').hide();
$('.mathjax-widget').keyup( function(){
  if (Preview.timeout) {clearTimeout(Preview.timeout)};
    textarea_value = $(this).val();
    Preview.preview = $(this).parent().find('.MathPreview').get();
    Preview.buffer = $(this).parent().find('.MathBuffer').get();
    Preview.timeout = setTimeout(function(){
        Preview.callback(textarea_value);
      },Preview.delay);
  });
})