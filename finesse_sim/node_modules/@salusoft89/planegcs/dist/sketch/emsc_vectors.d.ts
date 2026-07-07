import { DoubleVector, IntVector } from "../planegcs_dist/gcs_system";
import { ModuleStatic } from "../planegcs_dist/planegcs";
export declare function arr_to_intvec(gcs_module: ModuleStatic, arr: number[]): IntVector;
export declare function arr_to_doublevec(gcs_module: ModuleStatic, arr: number[]): DoubleVector;
export declare function emsc_vec_to_arr(vec: IntVector | DoubleVector): number[];
