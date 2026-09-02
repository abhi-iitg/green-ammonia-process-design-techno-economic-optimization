% Optional MATLAB sensitivity template for IITG users.
prices = [20 40 60 80 100 120];
lcoa = [0 0 0 0 0 0];
% Populate lcoa with exported Python/Aspen values before plotting.
figure; plot(prices,lcoa,'o-'); xlabel('Electricity price ($/MWh)'); ylabel('LCOA ($/t NH3)'); grid on;
