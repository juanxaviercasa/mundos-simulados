<?php
/**
 * Expone los campos de SEO (Rank Math o Yoast) en la REST API de WordPress
 * para que se puedan escribir al crear un post por API, en lugar de tener
 * que rellenarlos a mano desde el editor.
 *
 * Instalación: sube este archivo a wp-content/mu-plugins/
 * (crea esa carpeta si no existe). No necesita activarse, mu-plugins
 * se cargan siempre.
 */

add_action('init', function () {
    $campos = [
        // Rank Math
        'rank_math_title'          => 'string',
        'rank_math_description'    => 'string',
        'rank_math_focus_keyword'  => 'string',
        // Yoast (por si usas ese en vez de Rank Math)
        '_yoast_wpseo_title'       => 'string',
        '_yoast_wpseo_metadesc'    => 'string',
        '_yoast_wpseo_focuskw'     => 'string',
    ];

    foreach ($campos as $campo => $tipo) {
        register_post_meta('post', $campo, [
            'type'          => $tipo,
            'single'        => true,
            'show_in_rest'  => true,
            'auth_callback' => function () {
                return current_user_can('edit_posts');
            },
        ]);
    }
});
