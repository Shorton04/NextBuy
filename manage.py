FORM f_send_to_cpi.
  IF p_test = abap_true.
    RETURN. " Skip CPI call in test mode
  ENDIF.

  DATA: lv_payload   TYPE string,
        lv_content   TYPE string VALUE 'application/json',
        lv_rfc       TYPE rfcdest VALUE 'CMX_WorkOrder',
        lv_status    TYPE i,
        lv_status_c  TYPE char10,
        lv_response  TYPE string.

  " Build JSON payload (PascalCase)
  TRY.
      lv_payload = xco_ku_json=>data->from_abap( gt_output )->apply( VALUE #(
                        ( xco_ku_json=>transformation->underscore_to_pascal_case )
      ) )->to_string( ).
    CATCH cx_sxml_error INTO DATA(lx_error).
      LOOP AT gt_output ASSIGNING FIELD-SYMBOL(<ls_output_row>).
        <ls_output_row>-msg = |JSON build failed: { lx_error->get_text( ) }|.
        PERFORM f_write_log USING <ls_output_row>-aufnr
                                   <ls_output_row>-vornr
                                   <ls_output_row>-werks
                                   'CMXS'
                                   <ls_output_row>-msg.
      ENDLOOP.
      RETURN.
  ENDTRY.

  " HTTP client from destination
  cl_http_client=>create_by_destination(
    EXPORTING destination = lv_rfc
    IMPORTING client      = DATA(lo_http_client)
    EXCEPTIONS OTHERS     = 1 ).
  IF sy-subrc <> 0 OR lo_http_client IS INITIAL.
    LOOP AT gt_output ASSIGNING <ls_output_row>.
      <ls_output_row>-msg = 'HTTP client creation failed'.
      PERFORM f_write_log USING <ls_output_row>-aufnr
                                 <ls_output_row>-vornr
                                 <ls_output_row>-werks
                                 'CMXS'
                                 <ls_output_row>-msg.
    ENDLOOP.
    RETURN.
  ENDIF.

  " HTTP headers
  lo_http_client->request->set_header_field( name = '~request_method' value = 'POST' ).
  lo_http_client->request->set_header_field( name = 'Content-Type'    value = lv_content ).

  " Payload
  lo_http_client->request->set_cdata( lv_payload ).

  " Send + receive
  TRY.
      lo_http_client->send( ).
      lo_http_client->receive( ).
    CATCH cx_root INTO DATA(lx_comm_error).
      LOOP AT gt_output ASSIGNING <ls_output_row>.
        <ls_output_row>-msg = |HTTP error: { lx_comm_error->get_text( ) }|.
        PERFORM f_write_log USING <ls_output_row>-aufnr
                                   <ls_output_row>-vornr
                                   <ls_output_row>-werks
                                   'CMXS'
                                   <ls_output_row>-msg.
      ENDLOOP.
      RETURN.
  ENDTRY.

  " Status + response
  lo_http_client->response->get_status( IMPORTING code = lv_status ).
  WRITE lv_status TO lv_status_c.
  lv_response = lo_http_client->response->get_cdata( ).

  " Log
  LOOP AT gt_output ASSIGNING <ls_output_row>.
    IF lv_status = 200.
      <ls_output_row>-msg = 'CPI success'.
    ELSE.
      <ls_output_row>-msg = |CPI error { lv_status_c }: { lv_response }|.
    ENDIF.
    PERFORM f_write_log USING <ls_output_row>-aufnr
                               <ls_output_row>-vornr
                               <ls_output_row>-werks
                               'CMXS'
                               <ls_output_row>-msg.
  ENDLOOP.

  COMMIT WORK.
ENDFORM.