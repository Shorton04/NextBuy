FORM f_send_to_cpi .
  DATA: lv_payload TYPE string.
  DATA: lv_rfc TYPE rfcdest VALUE 'CMX_MaintenancePlan'.
  DATA: lv_content_value TYPE string VALUE 'application/json'.

  TRY.
      lv_payload = xco_ku_json=>data->from_abap( gt_payload )->apply( VALUE #(
                                ( xco_ku_json=>transformation->underscore_to_pascal_case )
      ) )->to_string( ).
    CATCH cx_sxml_error INTO DATA(lx_sxml_error).
  ENDTRY.

  CALL METHOD cl_http_client=>create_by_destination
    EXPORTING
      destination              = lv_rfc
    IMPORTING
      client                   = DATA(lo_http_client)
    EXCEPTIONS
      argument_not_found       = 1
      destination_not_found    = 2
      destination_no_authority = 3
      plugin_not_active        = 4
      internal_error           = 5
      OTHERS                   = 6.

  IF sy-subrc <> 0.

  ENDIF.

  CALL METHOD lo_http_client->request->set_header_field
    EXPORTING
      name  = '~request_method'
      value = 'POST'.

  CALL METHOD lo_http_client->request->set_header_field
    EXPORTING
      name  = 'Content-Type'
      value = lv_content_value.

  CALL METHOD lo_http_client->request->set_cdata
    EXPORTING
      data = lv_payload.

  CALL METHOD lo_http_client->send
    EXCEPTIONS
      http_communication_failure = 1
      http_invalid_state         = 2
      http_processing_failed     = 3
      http_invalid_timeout       = 4
      OTHERS                     = 5.
  IF sy-subrc <> 0.

  ENDIF.

  CALL METHOD lo_http_client->receive
    EXCEPTIONS
      http_communication_failure = 1
      http_invalid_state         = 2
      http_processing_failed     = 3
      OTHERS                     = 4.

  lo_http_client->response->get_status( IMPORTING code = DATA(lv_status) ).

  IF lv_status = '200'.

  ENDIF.

ENDFORM.
