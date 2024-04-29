% generate a scenario.

% the transmitted signal is a random signal of length N

% length of signal
N = 10000;

% a complex random signal
nn = randn(1, N) + j * randn(1, N);

scenarioNUM = 1

fs = 1e5;
t = ((1:length(nn))-1)/fs;

if (scenarioNUM == 1)
  % a second signal, which is a function of the first.
  nn2 = timeshift(nn, -100.5);
  nn2 = nn2 .* exp(j * 2 * pi *-100 * t);
end
% note: nn2 is a timeshifted and frequency shifted version of
% the first signal


%%%% Alternative configuration
if (scenarioNUM == 2)  % 3 'target' scenario

  nn2 = timeshift(nn, -20.5);
  nn2 = nn2 .* exp(j * 2 * pi * -100 * t);

  nn3 = timeshift(nn, -40.5);
  nn3 = nn3 .* exp(j * 2 * pi * -180 * t);

  nn4 = timeshift(nn, -80.5);
  nn4 = nn4 .* exp(j * 2 * pi * +100 * t);
  nn2 = nn2 + nn3 + nn4;

end
