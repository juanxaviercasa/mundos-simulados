<?php
/**
 * Plugin Name: MundoSimulados Suite AI - Ultimate Edition
 * Plugin URI:  https://mundosimulados.online
 * Description: Sistema autónomo e integral de creación, rotación de API Keys, SEO/GEO, generación de imágenes y monetización en lote.
 * Version:     2.0.0
 * Author:      Mundo Simulados Tech
 * Text Domain: mundosimulados-suite
 */

if (!defined('ABSPATH')) exit;

require_once __DIR__ . '/includes/class-research-manager.php';
require_once __DIR__ . '/includes/class-image-manager.php';

class MundoSimuladosSuiteUltimate {
    private $research_manager;
    private $image_manager;
    
    public function __construct() {
        $this->research_manager = new MundoSimuladosResearchManager();
        $this->image_manager = new MundoSimuladosImageManager();
        add_action('admin_menu', [$this, 'add_admin_menu']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('add_meta_boxes', [$this, 'add_custom_meta_box']);
        add_action('wp_ajax_ms_process_ai_action', [$this, 'process_ai_action']);
        add_action('wp_ajax_ms_bulk_process_posts', [$this, 'bulk_process_posts']);
        add_filter('cron_schedules', [$this, 'add_cron_schedule']);
        add_action('init', [$this, 'maybe_schedule_pipeline']);
        add_action('ms_generate_content_pipeline', [$this, 'generate_content_pipeline']);
        add_action('ms_process_editorial_job', [$this, 'process_editorial_job']);
    }

    // 1. Menús de Administración
    public function add_admin_menu() {
        add_menu_page(
            'MundoSimulados AI',
            'MS AI Ultimate',
            'manage_options',
            'mundosimulados-ai',
            [$this, 'render_admin_page'],
            'dashicons-shield',
            90
        );

        add_submenu_page(
            'mundosimulados-ai',
            'Procesador Masivo (Bulk)',
            '🚀 Dashboard Masivo',
            'manage_options',
            'ms-ai-bulk',
            [$this, 'render_bulk_page']
        );
    }

    public function register_settings() {
        register_setting('ms_ai_options', 'ms_gemini_api_keys', ['sanitize_callback' => [$this, 'sanitize_api_keys']]);
        register_setting('ms_ai_options', 'ms_gemini_model', ['sanitize_callback' => [$this, 'sanitize_model']]);
        register_setting('ms_ai_options', 'ms_enable_auto_images', ['sanitize_callback' => 'absint']);
        register_setting('ms_ai_options', 'ms_link_hostinger', ['sanitize_callback' => 'esc_url_raw']);
        register_setting('ms_ai_options', 'ms_link_siteground', ['sanitize_callback' => 'esc_url_raw']);
        register_setting('ms_ai_options', 'ms_link_ledger', ['sanitize_callback' => 'esc_url_raw']);
        register_setting('ms_ai_options', 'ms_link_custom', ['sanitize_callback' => 'esc_url_raw']);
        register_setting('ms_ai_options', 'ms_enable_content_pipeline', ['sanitize_callback' => 'absint']);
        register_setting('ms_ai_options', 'ms_pipeline_interval', ['sanitize_callback' => [$this, 'sanitize_pipeline_interval']]);
        register_setting('ms_ai_options', 'ms_research_providers', ['sanitize_callback' => [$this, 'sanitize_provider_order']]);
        register_setting('ms_ai_options', 'ms_brave_search_key', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_bing_search_key', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_google_search_key', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_google_search_cx', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_youtube_key', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_reddit_user_agent', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_search_console_token', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_search_console_site', ['sanitize_callback' => 'esc_url_raw']);
        register_setting('ms_ai_options', 'ms_bing_webmaster_key', ['sanitize_callback' => 'sanitize_text_field']);
        register_setting('ms_ai_options', 'ms_bing_webmaster_site', ['sanitize_callback' => 'esc_url_raw']);
    }

    public function sanitize_api_keys($value) {
        $keys = array_filter(array_map('trim', explode("\n", (string) $value)));
        return implode("\n", array_map('sanitize_text_field', $keys));
    }

    public function sanitize_model($value) {
        $allowed_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash'];
        return in_array($value, $allowed_models, true) ? $value : 'gemini-1.5-flash';
    }

    public function sanitize_pipeline_interval($value) {
        $allowed_intervals = ['six_hours', 'twice_daily', 'daily'];
        return in_array($value, $allowed_intervals, true) ? $value : 'daily';
    }

    public function sanitize_provider_order($value) {
        $allowed = ['search_console', 'bing_webmaster', 'brave', 'bing', 'google', 'youtube', 'reddit'];
        $providers = array_filter(array_map('sanitize_key', explode(',', (string) $value)));
        $providers = array_values(array_intersect($providers, $allowed));
        return implode(',', array_unique($providers));
    }

    public function add_cron_schedule($schedules) {
        $schedules['ms_six_hours'] = [
            'interval' => 6 * HOUR_IN_SECONDS,
            'display'  => 'Cada seis horas'
        ];
        return $schedules;
    }

    public function maybe_schedule_pipeline() {
        if (get_option('ms_enable_content_pipeline') !== '1') {
            wp_clear_scheduled_hook('ms_generate_content_pipeline');
            return;
        }

        $interval = get_option('ms_pipeline_interval', 'daily');
        $schedule = $interval === 'six_hours' ? 'ms_six_hours' : $interval;
        $scheduled_interval = get_option('ms_pipeline_scheduled_interval');
        if ($scheduled_interval !== $schedule && wp_next_scheduled('ms_generate_content_pipeline')) {
            wp_clear_scheduled_hook('ms_generate_content_pipeline');
        }

        if (!wp_next_scheduled('ms_generate_content_pipeline')) {
            wp_schedule_event(time() + 300, $schedule, 'ms_generate_content_pipeline');
            update_option('ms_pipeline_scheduled_interval', $schedule, false);
        }
    }

    // 2. Vista de Ajustes Principales
    public function render_admin_page() {
        ?>
        <div class="wrap">
            <h1>🛡️ MS AI Suite Ultimate - Configuración del Motor</h1>
            <p>Configura tu Pool de API Keys con conmutación automática, opciones de imágenes y enlaces de afiliado.</p>
            <form method="post" action="options.php">
                <?php
                settings_fields('ms_ai_options');
                do_settings_sections('ms_ai_options');
                ?>
                <table class="form-table">
                    <tr>
                        <th scope="row"><label for="ms_gemini_api_keys">Pool de Gemini API Keys (Rotación Automática):</label></th>
                        <td>
                            <textarea id="ms_gemini_api_keys" name="ms_gemini_api_keys" rows="5" class="large-text" placeholder="Pega aquí tus API Keys de Gemini, una por cada línea..."><?php echo esc_textarea(get_option('ms_gemini_api_keys')); ?></textarea>
                            <p class="description"><strong>Sistema Fallback Engine:</strong> Si una clave llega a su límite (HTTP 429), el plugin conmuta inmediatamente a la siguiente clave sin detener el proceso. Consigue claves gratis en <a href="https://aistudio.google.com/" target="_blank">Google AI Studio</a>.</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ms_gemini_model">Modelo de Gemini:</label></th>
                        <td>
                            <select id="ms_gemini_model" name="ms_gemini_model">
                                <option value="gemini-1.5-flash" <?php selected(get_option('ms_gemini_model'), 'gemini-1.5-flash'); ?>>Gemini 1.5 Flash (Gratuito y Veloz)</option>
                                <option value="gemini-1.5-pro" <?php selected(get_option('ms_gemini_model'), 'gemini-1.5-pro'); ?>>Gemini 1.5 Pro (Avanzado)</option>
                                <option value="gemini-2.0-flash" <?php selected(get_option('ms_gemini_model'), 'gemini-2.0-flash'); ?>>Gemini 2.0 Flash</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Auto-Generación de Imágenes:</th>
                        <td>
                            <label for="ms_enable_auto_images">
                                <input type="checkbox" id="ms_enable_auto_images" name="ms_enable_auto_images" value="1" <?php checked(get_option('ms_enable_auto_images'), '1'); ?> />
                                Generar y fijar Imagen Destacada automáticamente (vía Pollinations.ai API - 100% Gratis)
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Pipeline Editorial Automático:</th>
                        <td>
                            <label for="ms_enable_content_pipeline">
                                <input type="checkbox" id="ms_enable_content_pipeline" name="ms_enable_content_pipeline" value="1" <?php checked(get_option('ms_enable_content_pipeline'), '1'); ?> />
                                Generar cinco oportunidades y guardarlas como borradores
                            </label>
                            <p class="description">El Cron crea fichas completas, pero no publica. Para datos actuales hay que conectar una fuente de búsqueda o tendencias.</p>
                            <select name="ms_pipeline_interval">
                                <option value="six_hours" <?php selected(get_option('ms_pipeline_interval', 'daily'), 'six_hours'); ?>>Cada seis horas</option>
                                <option value="twice_daily" <?php selected(get_option('ms_pipeline_interval', 'daily'), 'twice_daily'); ?>>Dos veces al día</option>
                                <option value="daily" <?php selected(get_option('ms_pipeline_interval', 'daily'), 'daily'); ?>>Diariamente</option>
                            </select>
                            <?php $last_run = get_option('ms_pipeline_last_run'); ?>
                            <p class="description">Última ejecución: <?php echo $last_run ? esc_html($last_run) : 'todavía no ejecutado'; ?>. Borradores creados: <?php echo esc_html((string) get_option('ms_pipeline_last_created', 0)); ?>.</p>
                            <?php if (get_option('ms_pipeline_last_error')): ?>
                                <p style="color: #b32d2e;"><strong>Error:</strong> <?php echo esc_html(get_option('ms_pipeline_last_error')); ?></p>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row" colspan="2"><hr><h2>Fuentes de investigación</h2></th>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ms_research_providers">Orden de proveedores:</label></th>
                        <td>
                            <input type="text" id="ms_research_providers" name="ms_research_providers" value="<?php echo esc_attr(get_option('ms_research_providers', 'search_console,bing_webmaster,brave,bing,google,youtube,reddit')); ?>" class="regular-text" />
                            <p class="description">Separados por coma. Se prueban en orden y se salta temporalmente un proveedor con cuota agotada.</p>
                        </td>
                    </tr>
                    <tr><th scope="row"><label for="ms_brave_search_key">Brave Search API key:</label></th><td><input type="password" id="ms_brave_search_key" name="ms_brave_search_key" value="<?php echo esc_attr(get_option('ms_brave_search_key')); ?>" class="regular-text" autocomplete="new-password" /></td></tr>
                    <tr><th scope="row"><label for="ms_bing_search_key">Bing Web Search key:</label></th><td><input type="password" id="ms_bing_search_key" name="ms_bing_search_key" value="<?php echo esc_attr(get_option('ms_bing_search_key')); ?>" class="regular-text" autocomplete="new-password" /></td></tr>
                    <tr><th scope="row"><label for="ms_google_search_key">Google Custom Search key:</label></th><td><input type="password" id="ms_google_search_key" name="ms_google_search_key" value="<?php echo esc_attr(get_option('ms_google_search_key')); ?>" class="regular-text" autocomplete="new-password" /></td></tr>
                    <tr><th scope="row"><label for="ms_google_search_cx">Google Search Engine ID:</label></th><td><input type="text" id="ms_google_search_cx" name="ms_google_search_cx" value="<?php echo esc_attr(get_option('ms_google_search_cx')); ?>" class="regular-text" /></td></tr>
                    <tr><th scope="row"><label for="ms_youtube_key">YouTube Data API key:</label></th><td><input type="password" id="ms_youtube_key" name="ms_youtube_key" value="<?php echo esc_attr(get_option('ms_youtube_key')); ?>" class="regular-text" autocomplete="new-password" /></td></tr>
                    <tr><th scope="row"><label for="ms_reddit_user_agent">Reddit User-Agent:</label></th><td><input type="text" id="ms_reddit_user_agent" name="ms_reddit_user_agent" value="<?php echo esc_attr(get_option('ms_reddit_user_agent', 'MundoSimuladosSuite/1.0')); ?>" class="regular-text" /></td></tr>
                    <tr><th scope="row"><label for="ms_search_console_token">Search Console token:</label></th><td><input type="password" id="ms_search_console_token" name="ms_search_console_token" value="<?php echo esc_attr(get_option('ms_search_console_token')); ?>" class="regular-text" autocomplete="new-password" /><input type="url" name="ms_search_console_site" value="<?php echo esc_attr(get_option('ms_search_console_site', home_url('/'))); ?>" class="regular-text" placeholder="https://mundosimulados.online/" /></td></tr>
                    <tr><th scope="row"><label for="ms_bing_webmaster_key">Bing Webmaster key:</label></th><td><input type="password" id="ms_bing_webmaster_key" name="ms_bing_webmaster_key" value="<?php echo esc_attr(get_option('ms_bing_webmaster_key')); ?>" class="regular-text" autocomplete="new-password" /><input type="url" name="ms_bing_webmaster_site" value="<?php echo esc_attr(get_option('ms_bing_webmaster_site', home_url('/'))); ?>" class="regular-text" placeholder="https://mundosimulados.online/" /></td></tr>
                    <tr>
                        <th scope="row" colspan="2"><hr><h2>🔗 Enlaces de Afiliado Directos</h2></th>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ms_link_hostinger">Hostinger Link:</label></th>
                        <td><input type="url" id="ms_link_hostinger" name="ms_link_hostinger" value="<?php echo esc_attr(get_option('ms_link_hostinger')); ?>" class="regular-text" placeholder="https://www.hostinger.com/..." /></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ms_link_siteground">SiteGround Link:</label></th>
                        <td><input type="url" id="ms_link_siteground" name="ms_link_siteground" value="<?php echo esc_attr(get_option('ms_link_siteground')); ?>" class="regular-text" placeholder="https://www.siteground.com/..." /></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ms_link_ledger">Ledger Link:</label></th>
                        <td><input type="url" id="ms_link_ledger" name="ms_link_ledger" value="<?php echo esc_attr(get_option('ms_link_ledger')); ?>" class="regular-text" placeholder="https://www.ledger.com/..." /></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ms_link_custom">Custom Link (VPN/Cursos):</label></th>
                        <td><input type="url" id="ms_link_custom" name="ms_link_custom" value="<?php echo esc_attr(get_option('ms_link_custom')); ?>" class="regular-text" placeholder="https://..." /></td>
                    </tr>
                </table>
                <?php submit_button('Guardar Toda la Configuración'); ?>
            </form>
        </div>
        <?php
    }

    // 3. Vista del Dashboard Masivo (Bulk Operations)
    public function render_bulk_page() {
        $current_page = max(1, absint($_GET['paged'] ?? 1));
        $posts_per_page = 25;
        $search = sanitize_text_field(wp_unslash($_GET['s'] ?? ''));
        $requested_status = sanitize_key($_GET['post_status'] ?? 'all');
        $allowed_statuses = ['publish', 'draft', 'pending', 'future', 'private'];
        $post_status = in_array($requested_status, $allowed_statuses, true) ? $requested_status : $allowed_statuses;
        $query = new WP_Query([
            'post_type'      => 'post',
            'posts_per_page' => $posts_per_page,
            'paged'          => $current_page,
            'post_status'    => $post_status,
            's'              => $search,
            'orderby'        => 'date',
            'order'          => 'DESC'
        ]);
        $posts = $query->posts;
        ?>
        <div class="wrap">
            <h1>🚀 Dashboard de Procesamiento Masivo en Lote</h1>
            <p>Selecciona los artículos publicados que deseas auditar, monetizar o reescribir con IA en segundo plano.</p>

            <div style="background: #fff; padding: 15px; border: 1px solid #ccc; margin-bottom: 20px; border-radius: 4px;">
                <label><strong>Acción en Lote a Ejecutar:</strong></label>
                <select id="ms_bulk_action_type" style="margin-left: 10px; padding: 5px;">
                    <option value="monetization">1. Inyectar Bloque de Afiliación (Amenaza -> Solución)</option>
                    <option value="auto_image">2. Generar e Insertar Imagen Destacada AI</option>
                    <option value="seo_geo_rewrite">3. Reescribir con Optimización SEO & GEO (ChatGPT/SearchGPT Ready)</option>
                    <option value="lead_magnet">4. Insertar Caja Lead Magnet (Captura Email)</option>
                </select>
                <button type="button" id="ms_btn_start_bulk" class="button button-primary button-large" style="margin-left: 15px;">
                    ⚡ Iniciar Procesamiento Masivo
                </button>
            </div>

            <div id="ms_bulk_progress" style="display:none; margin-bottom: 15px; font-weight: bold; padding: 10px; background: #e7f4e8; border: 1px solid #46b450;">
                <span id="ms_bulk_status_text">Iniciando tareas...</span>
            </div>

            <form method="get" style="margin-bottom: 15px;">
                <input type="hidden" name="page" value="ms-ai-bulk" />
                <input type="search" name="s" value="<?php echo esc_attr($search); ?>" placeholder="Buscar por título..." />
                <select name="post_status">
                    <option value="all" <?php selected($requested_status, 'all'); ?>>Todos los estados</option>
                    <?php foreach ($allowed_statuses as $status): ?>
                        <option value="<?php echo esc_attr($status); ?>" <?php selected($requested_status, $status); ?>><?php echo esc_html(ucfirst($status)); ?></option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" class="button">Filtrar</button>
                <span style="margin-left: 10px;"><?php echo esc_html(number_format_i18n($query->found_posts)); ?> posts encontrados</span>
            </form>

            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <td class="manage-column column-cb check-column"><input type="checkbox" id="ms_select_all" /></td>
                        <th>Título del Artículo</th>
                        <th>Imagen Destacada</th>
                        <th>Estado de Monetización</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (!empty($posts)): ?>
                        <?php foreach ($posts as $p): 
                            $has_thumb = has_post_thumbnail($p->ID);
                            $has_monetization = $this->is_post_monetized($p);
                        ?>
                            <tr>
                                <th scope="row" class="check-column"><input type="checkbox" class="ms-post-cb" value="<?php echo $p->ID; ?>" /></th>
                                <td><strong><a href="<?php echo esc_url(get_edit_post_link($p->ID)); ?>" target="_blank"><?php echo esc_html($p->post_title); ?></a></strong></td>
                                <td><?php echo $has_thumb ? 'Con imagen' : 'Sin imagen'; ?></td>
                                <td><?php echo $has_monetization ? 'Monetizado' : 'Pendiente'; ?></td>
                                <td><?php echo get_the_date('Y/m/d', $p->ID); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr><td colspan="5">No se encontraron artículos.</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
            <?php if ($query->max_num_pages > 1): ?>
                <div class="tablenav bottom">
                    <?php echo wp_kses_post(paginate_links([
                        'base'      => add_query_arg('paged', '%#%', remove_query_arg('paged')),
                        'format'    => '',
                        'current'   => $current_page,
                        'total'     => $query->max_num_pages,
                        'type'      => 'list',
                        'prev_text' => '&laquo; Anterior',
                        'next_text' => 'Siguiente &raquo;'
                    ])); ?>
                </div>
            <?php endif; ?>
        </div>

        <script>
        jQuery(document).ready(function($) {
            $('#ms_select_all').on('change', function() {
                $('.ms-post-cb').prop('checked', $(this).prop('checked'));
            });

            $('#ms_btn_start_bulk').on('click', function() {
                var selected = [];
                $('.ms-post-cb:checked').each(function() {
                    selected.push($(this).val());
                });

                if (selected.length === 0) {
                    alert('Por favor selecciona al menos un artículo de la lista.');
                    return;
                }

                var actionType = $('#ms_bulk_action_type').val();
                var progressBox = $('#ms_bulk_progress');
                var statusText = $('#ms_bulk_status_text');

                progressBox.show();
                statusText.text('Iniciando procesamiento de ' + selected.length + ' artículos...');

                var currentIndex = 0;

                function processNext() {
                    if (currentIndex >= selected.length) {
                        statusText.html('🎉 ¡Proceso masivo completado con éxito para ' + selected.length + ' artículos! Recarga la página para ver cambios.');
                        return;
                    }

                    var postId = selected[currentIndex];
                    statusText.text('⏳ Procesando artículo (' + (currentIndex + 1) + '/' + selected.length + ') [ID: ' + postId + ']...');

                    $.post(ajaxurl, {
                        action: 'ms_bulk_process_posts',
                        post_id: postId,
                        action_type: actionType,
                        security: '<?php echo esc_js(wp_create_nonce('ms_ai_nonce_action')); ?>'
                    }, function(res) {
                        if (res.success) {
                            currentIndex++;
                            processNext();
                        } else {
                            statusText.html('❌ Error en Post ID ' + postId + ': ' + res.data + '. Continuando con el siguiente...');
                            currentIndex++;
                            setTimeout(processNext, 2000);
                        }
                    }).fail(function() {
                        statusText.html('❌ Error de conexión en Post ID ' + postId + '. Reintentando...');
                        setTimeout(processNext, 3000);
                    });
                }

                processNext();
            });
        });
        </script>
        <?php
    }

    // 4. Meta Box en el Editor Individual
    public function add_custom_meta_box() {
        add_meta_box('ms_ai_panel', '⚡ Suite de Monetización y SEO Ultimate', [$this, 'render_meta_box'], 'post', 'side', 'high');
    }

    public function render_meta_box($post) {
        wp_nonce_field('ms_ai_nonce_action', 'ms_ai_nonce');
        ?>
        <div style="padding: 10px 0;">
            <p><strong>Acción rápida para este post:</strong></p>
            <select id="ms_ai_action_type" style="width: 100%; margin-bottom: 10px;">
                <option value="monetization">1. Insertar Bloque Afiliados</option>
                <option value="auto_image">2. Generar e Insertar Imagen AI</option>
                <option value="seo_geo_rewrite">3. Optimización SEO/GEO Completa</option>
                <option value="lead_magnet">4. Crear Lead Magnet</option>
            </select>
            <button type="button" id="ms_ai_btn_run" class="button button-primary button-large" style="width: 100%;">
                Ejecutar Acción con Gemini
            </button>
            <div id="ms_ai_status" style="margin-top: 10px; font-weight: bold;"></div>
        </div>

        <script>
        jQuery(document).ready(function($) {
            $('#ms_ai_btn_run').on('click', function() {
                var actionType = $('#ms_ai_action_type').val();
                var postId = <?php echo $post->ID; ?>;
                var nonce = $('#ms_ai_nonce').val();
                var statusDiv = $('#ms_ai_status');

                statusDiv.css('color', '#0073aa').html('⏳ Procesando con IA...');

                $.post(ajaxurl, {
                    action: 'ms_process_ai_action',
                    post_id: postId,
                    action_type: actionType,
                    security: nonce
                }, function(response) {
                    if (response.success) {
                        statusDiv.css('color', '#46b450').html('✅ ¡Completado! Actualizando editor...');
                        location.reload();
                    } else {
                        statusDiv.css('color', '#dc3232').html('❌ Error: ' + response.data);
                    }
                });
            });
        });
        </script>
        <?php
    }

    // 5. Motor de Llamada a la API con Rotación (Fallback Engine)
    private function call_gemini_api_with_fallback($prompt) {
        $raw_keys = get_option('ms_gemini_api_keys', '');
        $keys = array_filter(array_map('trim', explode("\n", $raw_keys)));
        
        if (empty($keys)) {
            return new WP_Error('no_keys', 'No se han ingresado API Keys en la configuración.');
        }

        $model = get_option('ms_gemini_model', 'gemini-1.5-flash');

        foreach ($keys as $key) {
            $url = "https://generativelanguage.googleapis.com/v1beta/models/{$model}:generateContent?key={$key}";
            $body = ['contents' => [['parts' => [['text' => $prompt]]]]];

            $response = wp_remote_post($url, [
                'headers' => ['Content-Type' => 'application/json'],
                'body'    => wp_json_encode($body),
                'timeout' => 60,
            ]);

            if (is_wp_error($response)) {
                continue;
            }

            $code = wp_remote_retrieve_response_code($response);
            $data = json_decode(wp_remote_retrieve_body($response), true);

            if ($code === 200 && isset($data['candidates'][0]['content']['parts'][0]['text'])) {
                return $data['candidates'][0]['content']['parts'][0]['text'];
            }

            if ($code === 429 || $code === 403) {
                error_log('MS AI Suite: Una API Key devolvió un error temporal. Conmutando a la siguiente clave...');
                continue;
            }
        }

        return new WP_Error('all_keys_failed', 'Todas las API Keys de la lista están agotadas o devolvieron un error.');
    }

    public function generate_content_pipeline() {
        if (get_option('ms_enable_content_pipeline') !== '1' || get_transient('ms_pipeline_lock')) {
            return;
        }

        set_transient('ms_pipeline_lock', 1, 30 * MINUTE_IN_SECONDS);
        $existing_titles = get_posts([
            'post_type'      => 'post',
            'post_status'    => ['publish', 'draft', 'pending', 'future', 'private'],
            'posts_per_page' => -1,
            'fields'         => 'ids'
        ]);
        $title_list = [];
        foreach ($existing_titles as $existing_id) {
            $title_list[] = get_the_title($existing_id);
        }

        $prompt = "Actúa como estratega editorial para un sitio de seguridad digital, tecnología, privacidad y supervivencia digital.\n";
        $prompt .= "Genera exactamente cinco oportunidades de artículos que resuelvan necesidades actuales y no repitan los títulos existentes.\n";
        $prompt .= "La investigación en tiempo real no está conectada todavía: no inventes métricas ni afirmes búsquedas verificadas. Marca como 'requiere_verificacion' cualquier tendencia o dato actual.\n";
        $prompt .= "Devuelve únicamente JSON válido con esta estructura: {\"ideas\":[{\"title\":\"\",\"search_intent\":\"\",\"problem\":\"\",\"primary_keyword\":\"\",\"secondary_keywords\":[],\"seo_summary\":\"\",\"geo_questions\":[],\"affiliate_provider\":\"ledger|hostinger|siteground|custom|none\",\"image_prompts\":[\"featured\",\"internal_1\",\"internal_2\"],\"requires_verification\":true}]}\n";
        $prompt .= "No redactes todavía el artículo completo: esta tarea solo debe producir las cinco fichas y sus prompts de imágenes.\n";
        $providers = array_filter(array_map('sanitize_key', explode(',', get_option('ms_research_providers', 'search_console,bing_webmaster,brave,bing,google,youtube,reddit'))));
        $research = $this->research_manager->collect('seguridad digital privacidad tecnología supervivencia digital', $providers);
        $prompt .= "Resultados de investigación disponibles (úsalos como señales, no inventes datos): " . wp_json_encode($research, JSON_UNESCAPED_UNICODE) . "\n";
        $prompt .= "Títulos ya existentes (no repetir): " . implode(' | ', array_slice($title_list, 0, 500));

        $result = $this->call_gemini_api_with_fallback($prompt);
        if (is_wp_error($result)) {
            delete_transient('ms_pipeline_lock');
            update_option('ms_pipeline_last_error', sanitize_text_field($result->get_error_message()));
            return;
        }

        $json = trim(preg_replace('/^```(?:json)?|```$/m', '', $result));
        $data = json_decode($json, true);
        if (!is_array($data) || empty($data['ideas']) || !is_array($data['ideas'])) {
            delete_transient('ms_pipeline_lock');
            update_option('ms_pipeline_last_error', 'Gemini no devolvió el JSON editorial esperado.');
            return;
        }

        $created = 0;
        foreach (array_slice($data['ideas'], 0, 5) as $idea) {
            $title = sanitize_text_field($idea['title'] ?? '');
            if (!$title || $this->pipeline_title_exists($title)) {
                continue;
            }

            $affiliate_provider = sanitize_key($idea['affiliate_provider'] ?? 'none');
            $post_id = wp_insert_post([
                'post_title'   => $title,
                'post_content' => '<p>Fase editorial pendiente de generación.</p>',
                'post_excerpt' => sanitize_textarea_field($idea['seo_summary'] ?? ''),
                'post_status'  => 'draft',
                'post_type'    => 'post'
            ], true);

            if (is_wp_error($post_id)) {
                continue;
            }

            update_post_meta($post_id, '_ms_pipeline_status', 'draft_created');
            update_post_meta($post_id, '_ms_research_sources', $research);
            update_post_meta($post_id, '_ms_search_intent', sanitize_text_field($idea['search_intent'] ?? ''));
            update_post_meta($post_id, '_ms_problem_opportunity', sanitize_textarea_field($idea['problem'] ?? ''));
            update_post_meta($post_id, '_ms_primary_keyword', sanitize_text_field($idea['primary_keyword'] ?? ''));
            update_post_meta($post_id, '_ms_secondary_keywords', array_map('sanitize_text_field', (array) ($idea['secondary_keywords'] ?? [])));
            update_post_meta($post_id, '_ms_geo_questions', array_map('sanitize_text_field', (array) ($idea['geo_questions'] ?? [])));
            update_post_meta($post_id, '_ms_affiliate_provider', $affiliate_provider);
            update_post_meta($post_id, '_ms_image_prompts', array_map('sanitize_textarea_field', (array) ($idea['image_prompts'] ?? [])));
            update_post_meta($post_id, '_ms_requires_verification', !empty($idea['requires_verification']) ? '1' : '0');
            update_post_meta($post_id, '_ms_pipeline_job_scheduled', '1');
            wp_schedule_single_event(time() + ($created * 60), 'ms_process_editorial_job', [$post_id]);
            $created++;
        }

        update_option('ms_pipeline_last_run', current_time('mysql'));
        update_option('ms_pipeline_last_created', $created);
        delete_option('ms_pipeline_last_error');
        delete_transient('ms_pipeline_lock');
    }

    public function process_editorial_job($post_id) {
        $post_id = absint($post_id);
        $post = get_post($post_id);
        if (!$post || $post->post_type !== 'post' || get_post_meta($post_id, '_ms_pipeline_status', true) === 'completed') {
            return;
        }

        update_post_meta($post_id, '_ms_pipeline_status', 'processing');
        $prompts = array_values((array) get_post_meta($post_id, '_ms_image_prompts', true));
        if (get_option('ms_enable_auto_images') !== '1' || count($prompts) < 3) {
            update_post_meta($post_id, '_ms_pipeline_status', 'error');
            update_post_meta($post_id, '_ms_last_ai_error', 'Se requieren imágenes automáticas activas y tres prompts: destacada, interna 1 e interna 2.');
            return;
        }

        $featured_id = get_post_thumbnail_id($post_id);
        if (!$featured_id) {
            $featured_id = $this->image_manager->generate_and_attach($post_id, $prompts[0], true, 'featured');
        }
        $internal_ids = array_values(array_filter(array_map('absint', (array) get_post_meta($post_id, '_ms_internal_image_ids', true))));
        foreach (array_slice($prompts, 1, 2) as $index => $internal_prompt) {
            if (empty($internal_ids[$index])) {
                    $internal_id = $this->image_manager->generate_and_attach($post_id, $internal_prompt, false, 'internal-' . ($index + 1));
                if ($internal_id) {
                    $internal_ids[$index] = $internal_id;
                }
            }
        }
        $internal_ids = array_values(array_filter($internal_ids));
        if (!$featured_id || count($internal_ids) < 2) {
            update_post_meta($post_id, '_ms_pipeline_status', 'error');
            update_post_meta($post_id, '_ms_last_ai_error', 'No se pudieron generar las tres imágenes requeridas.');
            update_post_meta($post_id, '_ms_internal_image_ids', $internal_ids);
            return;
        }
        update_post_meta($post_id, '_ms_internal_image_ids', $internal_ids);

        $prompt = "Genera el artículo completo para el siguiente borrador editorial. Devuelve únicamente HTML limpio, sin Markdown ni etiquetas <html> o <body>.\n";
        $prompt .= "Título: " . $post->post_title . "\n";
        $prompt .= "Keyword principal: " . get_post_meta($post_id, '_ms_primary_keyword', true) . "\n";
        $prompt .= "Keywords secundarias: " . implode(', ', (array) get_post_meta($post_id, '_ms_secondary_keywords', true)) . "\n";
        $prompt .= "Intención de búsqueda: " . get_post_meta($post_id, '_ms_search_intent', true) . "\n";
        $prompt .= "Problema que debe resolver: " . get_post_meta($post_id, '_ms_problem_opportunity', true) . "\n";
        $prompt .= "Preguntas GEO: " . implode(' | ', (array) get_post_meta($post_id, '_ms_geo_questions', true)) . "\n";
        $prompt .= "Incluye introducción útil, respuesta directa para motores generativos, H2/H3, pasos prácticos, advertencias, conclusión y FAQ. No inventes estadísticas ni fuentes.\n";
        $prompt .= "Coloca exactamente estos marcadores, cada uno en su propia línea, en la sección donde la imagen aporte más contexto: [MS_IMAGE_INTERNAL_1] para ilustrar el primer concepto visual y [MS_IMAGE_INTERNAL_2] para ilustrar el segundo. No los coloques juntos, no los pongas en la introducción ni dentro de un encabezado, y no los cambies.\n";
        $prompt .= "Fuentes de investigación disponibles: " . wp_json_encode(get_post_meta($post_id, '_ms_research_sources', true), JSON_UNESCAPED_UNICODE);

        $result = $this->call_gemini_api_with_fallback($prompt);
        if (is_wp_error($result)) {
            update_post_meta($post_id, '_ms_pipeline_status', 'error');
            update_post_meta($post_id, '_ms_last_ai_error', sanitize_text_field($result->get_error_message()));
            return;
        }

        $content = wp_kses_post($result);
        if (strlen(wp_strip_all_tags($content)) < 300) {
            update_post_meta($post_id, '_ms_pipeline_status', 'error');
            update_post_meta($post_id, '_ms_last_ai_error', 'El artículo generado es demasiado corto.');
            return;
        }

        $content = $this->assemble_internal_images($post_id, $content, $internal_ids);
        $provider = sanitize_key(get_post_meta($post_id, '_ms_affiliate_provider', true));
        $content .= $this->build_affiliate_disclosure($provider);

        $updated = wp_update_post(['ID' => $post_id, 'post_content' => $content], true);
        if (is_wp_error($updated)) {
            update_post_meta($post_id, '_ms_pipeline_status', 'error');
            update_post_meta($post_id, '_ms_last_ai_error', sanitize_text_field($updated->get_error_message()));
            return;
        }

        update_post_meta($post_id, '_ms_pipeline_status', 'completed');
        update_post_meta($post_id, '_ms_last_ai_action', 'editorial_pipeline');
        delete_post_meta($post_id, '_ms_last_ai_error');
    }

    private function pipeline_title_exists($title) {
        return (bool) get_page_by_title($title, OBJECT, 'post');
    }

    private function assemble_internal_images($post_id, $content, $internal_ids) {
        foreach (array_values($internal_ids) as $index => $internal_id) {
            $marker = '[MS_IMAGE_INTERNAL_' . ($index + 1) . ']';
            $image_html = wp_get_attachment_image($internal_id, 'large', false, ['loading' => 'lazy']);
            if (!$image_html) {
                continue;
            }

            if (strpos($content, $marker) !== false) {
                $content = str_replace($marker, "\n\n" . $image_html . "\n\n", $content);
                update_post_meta($post_id, '_ms_image_placement_' . ($index + 1), 'contextual');
            } else {
                $content .= "\n\n" . $image_html;
                update_post_meta($post_id, '_ms_image_placement_' . ($index + 1), 'fallback_end');
            }
        }

        return $content;
    }

    private function build_affiliate_disclosure($provider) {
        $links = [
            'ledger'     => get_option('ms_link_ledger', ''),
            'hostinger'  => get_option('ms_link_hostinger', ''),
            'siteground' => get_option('ms_link_siteground', ''),
            'custom'     => get_option('ms_link_custom', '')
        ];
        if ($provider === 'none' || empty($links[$provider])) {
            return '';
        }

        $labels = [
            'ledger' => 'Ledger Hardware Wallet',
            'hostinger' => 'Hostinger',
            'siteground' => 'SiteGround',
            'custom' => 'Solución recomendada'
        ];
        return sprintf(
            "\n\n<section class=\"ms-affiliate-block\"><h2>Lecciones y medidas de protección</h2><p>Este artículo puede contener enlaces de afiliado. Si realizas una compra, el sitio podría recibir una comisión sin coste adicional para ti.</p><p><a href=\"%s\" target=\"_blank\" rel=\"nofollow sponsored\">Ver %s</a></p></section>",
            esc_url($links[$provider]),
            esc_html($labels[$provider])
        );
    }

    // 7. Procesadores AJAX
    public function process_ai_action() {
        check_ajax_referer('ms_ai_nonce_action', 'security');
        $this->execute_post_action(absint($_POST['post_id'] ?? 0), sanitize_key($_POST['action_type'] ?? ''));
    }

    public function bulk_process_posts() {
        check_ajax_referer('ms_ai_nonce_action', 'security');
        $this->execute_post_action(absint($_POST['post_id'] ?? 0), sanitize_key($_POST['action_type'] ?? ''));
    }

    private function execute_post_action($post_id, $action_type) {
        $allowed_actions = ['monetization', 'auto_image', 'seo_geo_rewrite', 'lead_magnet'];
        if (!in_array($action_type, $allowed_actions, true)) {
            wp_send_json_error('Acción no válida.');
        }

        $post = get_post($post_id);
        if (!$post || $post->post_type !== 'post') wp_send_json_error('Post no encontrado.');
        if (!current_user_can('edit_post', $post_id)) wp_send_json_error('No tienes permiso para editar este post.');

        if ($action_type === 'monetization' && $this->is_post_monetized($post)) {
            update_post_meta($post_id, '_ms_monetization_status', 'completed');
            wp_send_json_success(['output' => 'El post ya tiene monetización registrada.']);
        }

        if ($action_type === 'auto_image') {
            $success = has_post_thumbnail($post_id) || $this->image_manager->generate_and_attach($post_id, $post->post_title, true, 'featured');
            if ($success) {
                wp_send_json_success(['output' => 'Imagen generada y fijada correctamente.']);
            } else {
                wp_send_json_error('No se pudo generar la imagen.');
            }
        }

        $link_hostinger = get_option('ms_link_hostinger', '#');
        $link_siteground = get_option('ms_link_siteground', '#');
        $link_ledger = get_option('ms_link_ledger', '#');
        $link_custom = get_option('ms_link_custom', '#');

        $prompt = "Título: {$post->post_title}\nContenido: " . wp_strip_all_tags($post->post_content) . "\n\n";

        if ($action_type === 'monetization') {
            $prompt .= "Instrucción: Genera un bloque final HTML/Markdown titulado '### 🛡️ Lecciones y Medidas de Protección'.
            Si habla de finanzas/cripto/bancos, usa este enlace exacto: <a href='{$link_ledger}' target='_blank' rel='nofollow sponsored'>Ledger Hardware Wallet</a>.
            Si habla de redes/webs/infraestructura, usa este enlace: <a href='{$link_hostinger}' target='_blank' rel='nofollow sponsored'>Hostinger</a> o <a href='{$link_siteground}' target='_blank' rel='nofollow sponsored'>SiteGround</a>.
            Para otros casos usa: <a href='{$link_custom}' target='_blank' rel='nofollow sponsored'>Solución de Protección Recomendada</a>.";
        } elseif ($action_type === 'seo_geo_rewrite') {
            $prompt .= "Instrucción: Reescribe el artículo optimizándolo para SEO y GEO (Generative Engine Optimization). Incluye respuestas directas de 40 palabras para resúmenes de IA, estructura H2/H3 clara y una sección final de Preguntas Frecuentes (FAQ).";
        } elseif ($action_type === 'lead_magnet') {
            $prompt .= "Instrucción: Genera un bloque HTML estilizado con un formulario para descargar un PDF de Supervivencia Digital basado en este post.";
        }

        $result = $this->call_gemini_api_with_fallback($prompt);

        if (is_wp_error($result)) {
            update_post_meta($post_id, '_ms_last_ai_error', sanitize_text_field($result->get_error_message()));
            wp_send_json_error($result->get_error_message());
        }

        $safe_result = wp_kses_post($result);
        if ($action_type === 'monetization') {
            $safe_result = "<!-- ms:monetization:start -->\n" . $safe_result . "\n<!-- ms:monetization:end -->";
            update_post_meta($post_id, '_ms_monetization_status', 'completed');
            update_post_meta($post_id, '_ms_monetized_at', current_time('mysql'));
        }

        $updated_content = $action_type === 'seo_geo_rewrite'
            ? $safe_result
            : $post->post_content . "\n\n" . $safe_result;
        $update_result = wp_update_post([
            'ID'           => $post_id,
            'post_content' => $updated_content
        ], true);

        if (is_wp_error($update_result)) {
            update_post_meta($post_id, '_ms_last_ai_error', sanitize_text_field($update_result->get_error_message()));
            wp_send_json_error($update_result->get_error_message());
        }
        delete_post_meta($post_id, '_ms_last_ai_error');
        update_post_meta($post_id, '_ms_last_ai_action', $action_type);

        if (get_option('ms_enable_auto_images') == '1' && !has_post_thumbnail($post_id)) {
            $this->image_manager->generate_and_attach($post_id, $post->post_title, true, 'featured');
        }

        wp_send_json_success(['output' => $safe_result]);
    }

    private function is_post_monetized($post) {
        if (get_post_meta($post->ID, '_ms_monetization_status', true) === 'completed') {
            return true;
        }

        return strpos($post->post_content, '<!-- ms:monetization:start -->') !== false
            || strpos($post->post_content, 'Lecciones y Medidas de Protección') !== false;
    }

    public static function deactivate() {
        wp_clear_scheduled_hook('ms_generate_content_pipeline');
        wp_clear_scheduled_hook('ms_process_editorial_job');
        delete_transient('ms_pipeline_lock');
    }
}

register_deactivation_hook(__FILE__, ['MundoSimuladosSuiteUltimate', 'deactivate']);
new MundoSimuladosSuiteUltimate();