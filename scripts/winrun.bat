

:: "main" logic
set SIMPIPE_DIR="C:\Users\David Leon\Workspace\simpipe"
:: set gem5RISCVml_DIR="C:\Users\David Leon\workspace\gem5RISCVml"
set EXP_WORKSPACE_DIR="C:\Users\David Leon\Workspace\experiments\simpipe tables c win4 fixed LD"

echo simpipe Directory: %SIMPIPE_DIR%
echo gem5RISCVml Directory: %gem5RISCVml_DIR%
echo Experiment Directory: %EXP_WORKSPACE_DIR%

timeout /t 10

::call :coremark
::call :sha 
::call :qsort
call :dijekstra
::call :turbo_enc
::call :fft 


cd %EXP_WORKSPACE_DIR%

:: force execution to quit at the end of the "main" logic
EXIT /B %ERRORLEVEL%


:coremark
set EXPDIR=%EXP_WORKSPACE_DIR%\exp-0_multithread_coremark_rv64uc_num_threads_1__trace_off_1_
set MODEL=model_elu_brtk-ld-st_w-4_248-165-110_lr-1e-07

::cd %gem5RISCVml_DIR%
::python autoenc_riscv_ml/main.py mode=csvPredict bp=True tablesDir=%EXPDIR% modelFile=%EXPDIR%/%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=AETakenStats tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=winStatistics tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

cd %SIMPIPE_DIR%
start python src/main.py reg=1 dir=%EXPDIR%

EXIT /B 0



:sha
set EXPDIR=%EXP_WORKSPACE_DIR%\exp-0_multithread_sha_riscv64uc_num_threads_1__trace_off_1_
set MODEL=model_elu_brtk-ld-st_w-4_248-165-110_lr-1e-07

::cd %gem5RISCVml_DIR%
::python autoenc_riscv_ml/main.py mode=csvPredict bp=True tablesDir=%EXPDIR% modelFile=%EXPDIR%/%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=AETakenStats tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=winStatistics tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

cd %SIMPIPE_DIR%
start python src/main.py reg=1 dir=%EXPDIR%
EXIT /B 0


:qsort
set EXPDIR=%EXP_WORKSPACE_DIR%\exp-0_multithread_qsort_small_rv64uc_num_threads_1__trace_off_1_
set MODEL=model_elu_brtk-ld-st_w-4_248-124_lr-1e-08

::cd %gem5RISCVml_DIR%
::python autoenc_riscv_ml/main.py mode=csvPredict bp=True tablesDir=%EXPDIR% modelFile=%EXPDIR%/%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=AETakenStats tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=winStatistics tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

cd %SIMPIPE_DIR%
start python src/main.py reg=1 dir=%EXPDIR%
EXIT /B 0


:dijekstra
set EXPDIR=%EXP_WORKSPACE_DIR%\exp-0_multithread_dijkstra_small_rv64uc_num_threads_1__trace_off_1_
set MODEL=model_elu_brtk-ld-st_w-8_496-372-279_lr-1e-07

::cd %gem5RISCVml_DIR%
::python autoenc_riscv_ml/main.py mode=csvPredict bp=True tablesDir=%EXPDIR% modelFile=%EXPDIR%/%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=AETakenStats tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=winStatistics tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

cd %SIMPIPE_DIR%
start python src/main.py reg=1 dir=%EXPDIR%
EXIT /B 0


:fft
set EXPDIR=%EXP_WORKSPACE_DIR%\exp-0_multithread_fft_small_4_4096_0_uc_num_threads_1__trace_off_1_
set MODEL="model_elu_brtk-ld-st_w-2_124-103_lr-1e-08"

::cd %gem5RISCVml_DIR%
::python autoenc_riscv_ml/main.py mode=csvPredict bp=True tablesDir=%EXPDIR% modelFile=%EXPDIR%/%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=AETakenStats tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=winStatistics tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

cd %SIMPIPE_DIR%
start python src/main.py reg=1 dir=%EXPDIR%

EXIT /B 0


:turbo_enc
{

set EXPDIR=%EXP_WORKSPACE_DIR%\exp-0_multithread_tc_encoder_rv64_uc_num_threads_1__trace_off_1_
set MODEL="model_elu_brtk-ld-st_w-6_372-297_lr-1e-07"

::cd %gem5RISCVml_DIR%
::python autoenc_riscv_ml/main.py mode=csvPredict bp=True tablesDir=%EXPDIR% modelFile=%EXPDIR%/%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=AETakenStats tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

::cd %gem5RISCVml_DIR%
::start python autoenc_riscv_ml\main.py mode=winStatistics tablesDir=%EXPDIR% modelFile=%EXPDIR%\%MODEL%

cd %SIMPIPE_DIR%
start python src/main.py reg=1 dir=%EXPDIR%

EXIT /B 0
}



