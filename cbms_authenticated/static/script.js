

  $('#imageModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var imageUrl = button.data('image-url');
    var modal = $(this);
    modal.find('.modal-body #fullImage').attr('src', imageUrl);
  });

