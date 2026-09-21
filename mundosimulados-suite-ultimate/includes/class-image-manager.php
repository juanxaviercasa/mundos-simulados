<?php

if (!defined('ABSPATH')) {
    exit;
}

class MundoSimuladosImageManager {
    public function generate_and_attach($post_id, $prompt_text, $set_thumbnail = true, $image_role = 'featured') {
        $safe_prompt = rawurlencode('editorial illustration, no text, ' . substr($prompt_text, 0, 300));
        $image_url = "https://image.pollinations.ai/prompt/{$safe_prompt}?width=1200&height=630&nologo=true";
        $response = wp_safe_remote_get($image_url, ['timeout' => 30]);
        if (is_wp_error($response) || wp_remote_retrieve_response_code($response) !== 200) {
            return false;
        }

        $upload_dir = wp_upload_dir();
        $keyword = get_post_meta($post_id, '_ms_primary_keyword', true);
        $base_name = sanitize_title(get_the_title($post_id) . '-' . $keyword . '-' . $image_role);
        $filename = wp_unique_filename($upload_dir['path'], $base_name . '.jpg');
        $upload = wp_upload_bits($filename, null, wp_remote_retrieve_body($response));
        if ($upload['error']) {
            return false;
        }

        $filetype = wp_check_filetype($upload['file'], null);
        $alt_text = sanitize_text_field(get_the_title($post_id) . ' - ' . $image_role);
        $attachment_id = wp_insert_attachment([
            'post_mime_type' => $filetype['type'],
            'post_title'     => $alt_text,
            'post_content'   => '',
            'post_status'    => 'inherit'
        ], $upload['file'], $post_id, true);
        if (is_wp_error($attachment_id)) {
            return false;
        }

        require_once ABSPATH . 'wp-admin/includes/image.php';
        $metadata = wp_generate_attachment_metadata($attachment_id, $upload['file']);
        if (!$metadata) {
            return false;
        }
        wp_update_attachment_metadata($attachment_id, $metadata);
        update_post_meta($attachment_id, '_wp_attachment_image_alt', $alt_text);
        wp_update_post(['ID' => $attachment_id, 'post_excerpt' => $alt_text]);
        if ($set_thumbnail) {
            set_post_thumbnail($post_id, $attachment_id);
        }
        return $attachment_id;
    }
}
