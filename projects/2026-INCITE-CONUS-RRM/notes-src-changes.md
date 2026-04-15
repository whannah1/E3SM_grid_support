# Source Code changes for new grid definition

----------------------------------------------------------------------------------------------------

## cime_config/config_grids.xml

### XML grid spec - 

```xml
    <!--=====================================================================-->
    <!-- INCITE 2026 CONUS-RRM -->
    <model_grid alias="conus1024x2v1pg2_RRSwISC6to18E3r5">
      <grid name="atm">ne0np4_conus1024x2v1.pg2</grid>
      <grid name="lnd">ne0np4_conus1024x2v1.pg2</grid>
      <grid name="ocnice">RRSwISC6to18E3r5</grid>
      <grid name="rof">r0125</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>RRSwISC6to18E3r5</mask>
    </model_grid>
    <!--=====================================================================-->
```

### XML domain spec

```xml

    <!--=====================================================================-->
    <domain name="ne32np4.pg2">
      <nx>24576</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.lnd.ne32pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <file grid="ice|ocn" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.ocn.ne32pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <desc>ne32pg2</desc>
    </domain>
```

### XML map spec

```xml
    <!--=====================================================================-->
    <!-- INCITE 2026 CONUS-RRM  -->
    <!--=====================================================================-->
    <!-- ne32 -->
    <gridmap atm_grid="ne32np4.pg2" ocn_grid="RRSwISC6to18E3r5">
      <map name="ATM2OCN_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_traave.20251006.nc</map>
      <map name="ATM2OCN_VMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="ATM2OCN_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="OCN2ATM_FMAPNAME"          >cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne32pg2_traave.20251006.nc</map>
      <map name="OCN2ATM_SMAPNAME"          >cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne32pg2_traave.20251006.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne32np4.pg2" lnd_grid="r025">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trbilin.20251006.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_r025_to_ne32pg2_traave.20251006.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_r025_to_ne32pg2_traave.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne32np4.pg2" rof_grid="r025">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trbilin.20251006.nc</map>
    </gridmap>

    <!--=====================================================================-->

```

----------------------------------------------------------------------------------------------------

## components/eam/bld/config_files/horiz_grid.xml

```xml
<!--=====================================================================-->
<!-- 2025 SciDAC grids for multi-fidelity study  -->
<horiz_grid dyn="se" hgrid="ne0np4_CONUS2026-1024x2" ncol="152714" csne="0" csnp="4" npg="0" />
<!--=====================================================================-->
```