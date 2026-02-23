function analog_browser()
    % --- Settings ---
    BASE_URL = 'https://raw.githubusercontent.com/gmakkena/analog-design-data/main/';
    FILE_MAP = {
        'Efficiency vs. Bias (gm/ID vs VGS)', 'gmoverid_vs_vgs.csv';
        'Efficiency vs. Density (gm/ID vs ID/W)', 'gmoverid_vs_idbyw.csv';
        'Intrinsic Gain vs. Density (gm/gds vs ID/W)', 'gmovergds_vs_idbyw.csv';
        'Gain vs. Efficiency (gm/gds vs gm/ID)', 'gmovergds_vs_gmoverid.csv';
        'Output Conductance (gds/ID vs ID/W)', 'gdsbyid_vs_idbyw.csv';
        'Transconductance (gm vs VGS)', 'gm_vs_vgs.csv'
    };

    % --- UI Construction ---
    fig = uifigure('Name', 'Analog IC Design Browser (Linear Scale)', 'Position', [100, 100, 1000, 750]);
    
    pnl = uipanel(fig, 'Position', [20, 670, 960, 60], 'Title', 'Controls');
    uilabel(pnl, 'Position', [10, 15, 150, 22], 'Text', 'Select Characterization:', 'FontWeight', 'bold');
    
    dd = uidropdown(pnl, 'Position', [160, 15, 350, 22], ...
        'Items', FILE_MAP(:,1), ...
        'ValueChanged', @(dd, event) update_plot(dd.Value));

    ax = uiaxes(fig, 'Position', [80, 80, 850, 560]);
    grid(ax, 'on'); 
    ax.XMinorGrid = 'on'; 
    ax.YMinorGrid = 'on';
    hold(ax, 'on');

    update_plot(FILE_MAP{1,1});

    % --- Plotting Engine ---
    function update_plot(selected_text)
        cla(ax);
        idx = find(strcmp(FILE_MAP(:,1), selected_text));
        filename = FILE_MAP{idx, 2};
        
        try
            legend(ax, 'off');
            data = readtable([BASE_URL, filename], 'VariableNamingRule', 'preserve');
            colors = lines(width(data)/2);
            
            for i = 1:2:width(data)
                x = data{:, i}; y = data{:, i+1};
                mask = ~isnan(x) & ~isnan(y);
                
                header = data.Properties.VariableNames{i};
                L_match = regexp(header, 'L=([\d\.e-]+)', 'tokens');
                L_label = sprintf('L = %.0fnm', str2double(L_match{1}{1}) * 1e9);
                
                plot(ax, x(mask), y(mask), '-o', ...
                     'LineWidth', 0.8, ...
                     'MarkerSize', 2.5, ...
                     'MarkerFaceColor', colors((i+1)/2, :), ...
                     'Color', colors((i+1)/2, :), ...
                     'DisplayName', L_label);
            end
            
            % Axis Styling
            title(ax, selected_text, 'FontSize', 13);
            set(ax, 'XScale', 'linear', 'YScale', 'linear');
            
            % --- X-AXIS RESTRICTION FOR ID/W (Max 300) ---
            if contains(filename, 'idbyw')
                xlim(ax, [0, 300]); % Restricts X-axis from 0 to 300
            else
                xlim(ax, 'auto');   % Default for other plots
            end

            % --- SMART LABELING ---
            if contains(filename, 'vgs')
                xlabel(ax, 'Gate-Source Voltage V_{GS} (V)');
            elseif contains(filename, 'idbyw')
                xlabel(ax, 'Current Density I_D/W (A/m)');
            elseif contains(filename, 'gmoverid')
                xlabel(ax, 'Efficiency g_m/I_D (V^{-1})');
            end

            if contains(filename, 'gmovergds')
                ylabel(ax, 'Intrinsic Gain g_m/g_{ds} (V/V)');
            elseif strncmp(filename, 'gmoverid', 8) && ~contains(filename, 'gmovergds')
                ylabel(ax, 'Efficiency g_m/I_D (V^{-1})');
            elseif contains(filename, 'gdsbyid')
                ylabel(ax, 'Output Conductance g_{ds}/I_D (V^{-1})');
            elseif contains(filename, 'gm_vs')
                ylabel(ax, 'Transconductance g_m (S)');
            end
            
            lgd = legend(ax, 'Location', 'northeastoutside', 'FontSize', 9);
            lgd.ItemHitFcn = @(src, event) set(event.Peer, 'Visible', ...
                char(string(setdiff({'on','off'}, event.Peer.Visible))));
            
        catch
            uialert(fig, 'Could not fetch data from GitHub.', 'Connection Error');
        end
    end
end
